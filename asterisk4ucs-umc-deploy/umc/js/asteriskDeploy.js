/*
Copyright (C) 2012 DECOIT GmbH <asterisk4ucs@decoit.de>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3 as
published by the Free Software Foundation

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
*/

dojo.provide("umc.modules.asteriskDeploy");

dojo.require("umc.widgets.Module");

dojo.declare("umc.modules.asteriskDeploy", [ umc.widgets.Module ], {
	_page: null,
	_form: null,
	_serverSelect: null,
	_serverdn: null,

	i18nClass: "umc.modules.asteriskDeploy",

	buildRendering: function () {
		this.inherited(arguments);

		this._page = new umc.widgets.Page({
			headerText: "Deployment von Asterisk-Konfigurationen",
		});
		this.addChild(this._page);

		var widgets = [{
			type: 'ComboBox',
			name: 'server',
			label: "Server",
			dynamicValues: "asteriskDeploy/queryServers",
// ssh-copy-id is not supported yet
//		}, {
//			type: 'Button',
//			name: 'copyid',
//			label: "SSH-Schlüssel kopieren",
//			callback: dojo.hitch(this, function () {
//				var rootpw = prompt("Root-Passwort des Asterisk-Servers?");
//				if (!rootpw || !rootpw.length)
//					return;
//
//				this._startAction("asteriskDeploy/copyid", {
//					server: this._serverdn,
//					rootpw: rootpw,
//				});
//			}),
		}, {
			type: 'Button',
			name: 'create',
			label: "Konfiguration testen",
			callback: dojo.hitch(this, function () {
				this._startAction("asteriskDeploy/create", {
					server: this._serverdn,
				});
			}),
		}, {
			type: 'Button',
			name: 'deploy',
			label: "Konfiguration anwenden",
			callback: dojo.hitch(this, function () {
				this._startAction("asteriskDeploy/deploy", {
					server: this._serverdn,
				});
			}),
		}];

		var layout = [
			[ "server", "copyid" ],
			[ "create", "deploy" ],
		];

		this._form = new umc.widgets.Form({
			widgets: widgets,
			layout: layout,
			region: "top",
		});
		this._page.addChild(this._form);
		
		this._log = new umc.widgets.Text({
			style: "font-family: monospace; overflow: scroll; white-space: pre;",
		});

		var container = new umc.widgets.ExpandingTitlePane({
			title: "Letzte Logdatei",
		});
		this._page.addChild(container);
		container.addChild(this._log);

		asteriskDeploy = this;
	},
	postCreate: function () {
		this.inherited(arguments);

		this._serverSelect = this._form.getWidget("server");
		this._serverdn = this._serverSelect.getValue();

		dojo.connect(this._serverSelect, "onChange", dojo.hitch(this, function () {
			this._setServer(this._serverSelect.getValue());
		}));
	},
	_setServer: function (serverdn) {
		this._serverdn = serverdn;
		this._refreshLog();
	},
	_startAction: function (action, args) {
		this._form.getWidget("server")._setDisabledAttr(true);
		this._form.getWidget("copyid")._setDisabledAttr(true);
		this._form.getWidget("create")._setDisabledAttr(true);
		this._form.getWidget("deploy")._setDisabledAttr(true);
		
		var call = this.umcpCommand(action, args);
		call.then(dojo.hitch(this, function (data) {
			this._stopAction();
			umc.dialog.notify("Befehl ausgeführt; Siehe Logdatei im unteren Teil des Fensters");
		}), dojo.hitch(this, function (data) {
			this._stopAction();
			umc.dialog.notify("Fehler!");
		}));
	},
	_stopAction: function () {
		this._form.getWidget("server")._setDisabledAttr(false);
		this._form.getWidget("copyid")._setDisabledAttr(false);
		this._form.getWidget("create")._setDisabledAttr(false);
		this._form.getWidget("deploy")._setDisabledAttr(false);

		this._refreshLog();
	},
	_refreshLog: function () {
		this._log._setContentAttr("[Logdatei lädt...]");

		var call = this.umcpCommand("asteriskDeploy/getLog", {
			server: this._serverdn,
		});
		call.then(dojo.hitch(this, function (data) {
			this._log._setContentAttr(data.result);
		}));
	},
});
