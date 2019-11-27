import {
	createConnection,
	TextDocuments,
	TextDocument,
	Diagnostic,
	DiagnosticSeverity,
	ProposedFeatures,
	InitializeParams,
	DidChangeConfigurationNotification,
	CompletionItem,
	CompletionItemKind,
	TextDocumentPositionParams
} from 'vscode-languageserver';

import * as fs from 'fs';
import * as path from 'path';
import { Server } from 'http';

// Create a connection for the server. The connection uses Node's IPC as a transport
let connection= createConnection(ProposedFeatures.all);

// Listen on the connection

let documents: TextDocuments = new TextDocuments();

let hasConfigurationCapability:boolean = false;
let hasWorkspaceFolderCapability:boolean = false;
let hasDiagnosticRelatedInformationCapability: boolean = false;



connection.onInitialize((params:InitializeParams) => {
	console.log('starting connection!');
	let capabilities = params.capabilities;
	hasConfigurationCapability = !!(
		capabilities.workspace && !!capabilities.workspace.configuration
	);
	hasWorkspaceFolderCapability = !!(
		capabilities.workspace && !!capabilities.workspace.workspaceFolders
	);

	hasDiagnosticRelatedInformationCapability = !!(
		capabilities.textDocument &&
		capabilities.textDocument.publishDiagnostics &&
		capabilities.textDocument.publishDiagnostics.relatedInformation
	);


	return {
		capabilities :{
			textDocumentSync : documents.syncKind,
		}
	}
});

connection.onInitialized(() => {
	if(hasConfigurationCapability) {
		connection.client.register(DidChangeConfigurationNotification.type, undefined)
	}
	if(hasWorkspaceFolderCapability) {
		connection.workspace.onDidChangeWorkspaceFolders(_event => {
			connection.console.log("Workspace folder change event received");
		});
	}

});

interface ServerSettings {
	connectionType : string;
	serverIp : string;
	serverPort: number;
};

const defaultSettings:ServerSettings = {
	connectionType : "sockets",
	serverIp : "127.0.0.1",
	serverPort : 1338
};

let globalSettings:ServerSettings = defaultSettings;
let documentSettings: Map<string, Thenable<ServerSettings>> = new Map();

connection.onDidChangeConfiguration(change => {
	if(hasConfigurationCapability) {
		documentSettings.clear();
	}
	else {
		globalSettings = <ServerSettings>((change.settings.td_completes_me || defaultSettings));
	}
});

function getDocumentSettings(resource: string): Thenable<ServerSettings> {

	if(!hasConfigurationCapability) {
		return Promise.resolve(globalSettings);
	}
	let result = documentSettings.get(resource);
	if(!result) {
		result = connection.workspace.getConfiguration({
			scopeUri: resource,
			section: 'tdCompletesMe'
		})
		documentSettings.set(resource, result);
	}
	return result;
}

documents.onDidClose(e => {
	documentSettings.delete(e.document.uri);
});

documents.listen(connection);
connection.listen();
