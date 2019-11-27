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
	TextDocumentPositionParams,
	IPCMessageReader,
	IPCMessageWriter
} from 'vscode-languageserver';

import * as fs from 'fs';
import * as path from 'path';
import { Server, request } from 'http';

import axios from 'axios';

// Create a connection for the server. The connection uses Node's IPC as a transport
let connection= createConnection(new IPCMessageReader(process), new IPCMessageWriter(process));

// Listen on the connection

let documents: TextDocuments = new TextDocuments();

let hasConfigurationCapability:boolean = false;
let hasWorkspaceFolderCapability:boolean = false;
let hasDiagnosticRelatedInformationCapability: boolean = false;



connection.onInitialize((params:InitializeParams) => {
	connection.console.log('starting connection!');
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
		capabilities: {
			textDocumentSync: documents.syncKind,
			// Tell the client that the server supports code completion
			completionProvider: {
				resolveProvider: true
			}
		}
	};
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
	console.log('server initialized');
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
		console.log('configuration changed');
});


connection.onCompletion((_position : TextDocumentPositionParams) : CompletionItem[] => {

	console.log('completion');
	let document_name = "some_doc.py";
	let line = 'op("someop").method';

	let completions= []; 

	axios.post('http://localhost:1338', JSON.stringify({document_name,line})).then(
		(res) => {
		return  [
		{
			label : 'TypeScript',
			kind: CompletionItemKind.Text,
			data: 1
		},
		{
			label : 'Javascript',
			kind: CompletionItemKind.Text,
			data: 2
		},
		{
			label: 'Hello Complete',
			kind:CompletionItemKind.Text,
			data:3
		}
	] 
		}).catch( (err) => {
			console.log(err);
			return [];
		}).finally( () => {
			return [];
		});

		return [];
});


connection.onCompletionResolve(
	(item: CompletionItem): CompletionItem => {
		if (item.data === 1) {
			item.detail = 'TypeScript details';
			item.documentation = 'TypeScript documentation';
		} else if (item.data === 2) {
			item.detail = 'JavaScript details';
			item.documentation = 'JavaScript documentation';
		}
		else{
			item.detail = "deets"
			item.documentation =  "docs"
		}
		return item;
	}
);



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



documents.onDidOpen(e=> {
	console.log("opened : " + e.document.uri);
});

documents.onDidClose(e => {
	documentSettings.delete(e.document.uri);
});

documents.listen(connection);
connection.listen();
