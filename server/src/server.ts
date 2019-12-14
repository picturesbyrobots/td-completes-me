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
	IPCMessageWriter,
	Position,
	VersionedTextDocumentIdentifier,
	Range
} from 'vscode-languageserver';

import * as fs from 'fs';
import * as path from 'path';
import { Server, request } from 'http';

import axios from 'axios';
import * as vscode from 'vscode';

// Create a connection for the server. The connection uses Node's IPC as a transport
let connection= createConnection(new IPCMessageReader(process), new IPCMessageWriter(process));

// Listen on the connection

let documents: TextDocuments = new TextDocuments();

let hasConfigurationCapability:boolean = false;
let hasWorkspaceFolderCapability:boolean = false;
let hasDiagnosticRelatedInformationCapability: boolean = false;

let completionBuffer:CompletionItem[] = 

		[
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
				resolveProvider: true,
				triggerCharacters : ['.', '(', "'",'[']
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


export async function requestCompletionsFromTd(document_name:string, line:string)  {
	console.log('getting a completion');
	let results  = axios.post('http://localhost:1338', JSON.stringify({document_name,line})).then(
		(res) => {
			return res;
		});
	console.log(results);
}

connection.onCompletion(async (_position : TextDocumentPositionParams) : Promise<CompletionItem[]> => {

	let results:any = [];
	let current_document = documents.get(_position.textDocument.uri);
	let lines:any = []
	let char = _position.position.character;
	let line_idx = _position.position.line

	
	if(current_document) {
		lines = current_document.getText().split(/\r?\n/g);
		if( lines.length === 0) { 
			return results;
		}
	}


	interface ResData {
		label : string;
		kind : CompletionItemKind;
		detail : string;
		documentation: string;
	}
		results = await axios.post('http://localhost:1338', JSON.stringify({current_document , lines,line_idx, char})+ "\n").then(
		(res) => {
			let splits = res.data.split("\n\r\n\r")
			if(splits.length > 1) {

				let res_data = JSON.parse(splits[1]);
				console.log(res_data)
				let data_index = 0;
				let completion_data = res_data.map((result:ResData) => {
					return {label : result.label, 
						kind:result.kind, 
						documentation:result.documentation, 
						detail : result.detail}});
				
				return completion_data;
			} else {
				return [];
			}
		}).catch( (err) => {
			console.log(err);
			return [];
		}).finally( () => {
			return [];
		});

		console.log("results " +JSON.stringify(results))
		return results;
});


connection.onCompletionResolve(
	(item: CompletionItem): CompletionItem => {
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
