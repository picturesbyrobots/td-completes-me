'use strict'


import {EventEmitter}  from 'events' ;

const Net = require('net');
export class TDAdapter extends EventEmitter {

	private _pipe = new Net.Socket();
	private _host = "127.0.0.1";
	private _port = 1337

	private _connected = false;
	private _init = true;
	private _finished = false;



	private _requestQ= new Array<Object>()

	constructor() {
		super();
	}


	
}


