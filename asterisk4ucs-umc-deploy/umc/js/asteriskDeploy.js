/*global define*/
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

define([
	"umc/widgets/Module",
	"dojo/_base/declare",
	"dojo/_base/lang",
	"umc/widgets/Page",
	"umc/widgets/Form",
	"umc/widgets/Text",
	"umc/widgets/ExpandingTitlePane",
	"umc/dialog",
	"dojo/_base/array",
	"dojo/on",
	"umc/tools",
	"umc/i18n!umc/modules/asteriskDeploy"
],
function(Module,declare,lang,Page,Form,Text,ExpandingTitlePane,dialog,array,on,tools,asteriskDeploy,_){
	return declare("umc.modules.asteriskDeploy",[Module], {
		_page: null,
		_form: null,
		_serverSelect: null,
		_serverdn: null,
		umcpCommand: tools.umcpCommand,
		asteriskDeploy: null,
		i18nClass: "umc.modules.asteriskDeploy",

		buildRendering: function () {
			this.inherited(arguments);

			this._page = new Page({
				headerText: "Deployment von Asterisk-Konfigurationen"
			});
			this.addChild(this._page);

			var widgets = [{
				type: 'ComboBox',
				name: 'server',
				label: "Server",
				dynamicValues: "asteriskDeploy/queryServers"
	// ssh-copy-id is not supported yet
	//		}, {
	//			type: 'Button',
	//			name: 'copyid',
	//			label: "SSH-Schlüssel kopieren",
	//			callback: lang.hitch(this, function () {
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
				callback: lang.hitch(this, function () {
					this._startAction("asteriskDeploy/create", {
						server: this._serverdn = this._form.getWidget("server").get("value")
					});
				})
			}, {
				type: 'Button',
				name: 'deploy',
				label: "Konfiguration anwenden",
				callback: lang.hitch(this, function () {
					this._startAction("asteriskDeploy/deploy", {
						server: this._serverdn = this._form.getWidget("server").get("value")
					});
				})
			}];

			var layout = [
	//			[ "server", "copyid" ],
				[ "server" ],
				[ "create", "deploy" ]
			];

			this._form = new Form({
				widgets: widgets,
				layout: layout,
				region: "top"
			});
			this._page.addChild(this._form);
		
			this._log = new Text({
				style: "font-family: monospace; overflow: scroll; white-space: pre;"
			});

			var container = new ExpandingTitlePane({
				title: "Letzte Logdatei"
			});
			this._page.addChild(container);
			container.addChild(this._log);

			asteriskDeploy = this;
		},
		postCreate: function () {
			this.inherited(arguments);

			this._serverSelect = this._form.getWidget("server");
			//this._serverSelect.set("value","Testserver");
			this._serverdn = this._form.getWidget("server").get("value");
			//console.debug(this._serverdn);

			/*on(this._serverSelect, "onChange", lang.hitch(this, function () {
				this._setServer(this._form.getWidget("server").get("value"));
			}));*/
			this._serverSelect.watch("value", lang.hitch(this, function () {
				this._setServer(this._form.getWidget("server").get("value"));
			}));
		},
		_setServer: function (serverdn) {
			this._serverdn = serverdn;
			this._refreshLog();
		},
		_startAction: function (action, args) {

			this._form.getWidget("server")._setDisabledAttr(true);
	//		this._form.getWidget("copyid")._setDisabledAttr(true);
			this._form.getWidget("create")._setDisabledAttr(true);
			this._form.getWidget("deploy")._setDisabledAttr(true);
			//console.debug(uneval(args));
			var call = tools.umcpCommand(action, args);
			this._serverdn = this._form.getWidget("server").get("value");
			call.then(lang.hitch(this, function (data) {
				this._stopAction();
				dialog.notify("Befehl ausgeführt; Siehe Logdatei im unteren Teil des Fensters");
			}), lang.hitch(this, function (data) {
				this._stopAction();
				dialog.notify(this._form.getWidget("server").get("value"));
			}));
		},
		_stopAction: function () {

			this._form.getWidget("server")._setDisabledAttr(false);
	//		this._form.getWidget("copyid")._setDisabledAttr(false);
			this._form.getWidget("create")._setDisabledAttr(false);
			this._form.getWidget("deploy")._setDisabledAttr(false);

			this._refreshLog();
		},
		_refreshLog: function () {
			this._log._setContentAttr("[Logdatei lädt...]");

			var call = tools.umcpCommand("asteriskDeploy/getLog", {
				server: this._serverdn
			});
			call.then(lang.hitch(this, function (data) {
				this._log._setContentAttr(data.result);
			}));
		}
	});
});
