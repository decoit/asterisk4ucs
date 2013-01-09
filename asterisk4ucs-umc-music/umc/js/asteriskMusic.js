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
	"dojo/_base/declare",
	"dojo/_base/lang",
	"dojo/_base/array",
	"umc/widgets/TabbedModule",
	"umc/widgets/Module",
	"umc/widgets/ContainerWidget",
	"umc/widgets/Page",
	"umc/widgets/Form",
	"umc/widgets/Grid",
	"umc/widgets/ExpandingTitlePane",
	"umc/store",	
	"umc/widgets/Text",
	"umc/dialog",
	"dojo/on",
	"umc/tools",
	"umc/i18n!umc/modules/asteriskMusic"
],
function(declare,lang,array,TabbedModule,Module,ContainerWidget,Page,Form,Grid,ExpandingTitlePane,store,Text,dialog,on,tools,_){
	return declare("umc.modules.asteriskMusic",[Module],{
		_page: null,
		_form: null,
		_serverSelect: null,
		_serverdn: null,
		_mohSelect: null,
		_mohdn: null,
		_upload: null,
		_filename: null,
		umcpCommand: tools.umcpCommand,

		i18nClass: "umc.modules.asteriskMusic",



		buildRendering: function () {
			this.inherited(arguments);

			this._page = new Page({
				headerText: "Warteschlangenmusikverwaltungstool"
			});
			this.addChild(this._page);

			var widgets = [{
				type: 'ComboBox',
				name: 'server',
				label: "Server",
				dynamicValues: "asteriskMusic/queryServers"
			}, {
				type: 'ComboBox',
				name: 'moh',
				label: "Musikklasse",
				dynamicValues: "asteriskMusic/queryMohs",
				dynamicOptions: function (values) {
					return { serverdn: values.server };
				},
				depends: [
					"server"
				]
			}, {
				type: 'Button',
				name: 'create',
				label: "Musikklasse anlegen",
				callback: lang.hitch(this, function () {
					this.postCreate();
					var name = prompt("Bitte geben Sie den Namen für die neue Musikklasse ein:");
					if (!name) {
						dialog.alert("Ungültiger Name.");
						return;
					}
					/*this._serverSelect = this._form.getWidget("server");
					this._serverdn = this._serverSelect.getValue();*/
					var call = this.umcpCommand("asteriskMusic/create", {
						name: name,
						server: this._serverdn = this._form.getWidget("server").get("value")
					});
					call.then(lang.hitch(this, function (data) {
						dialog.notify("Musikklasse wurde angelegt.");

						this._mohSelect.setInitialValue(data.result.newDn, false);
						this._setServer(this._serverdn = this._form.getWidget("server").get("value"));
					}));
				})
			}, {
				type: 'Button',
				name: 'delete',
				label: "Musikklasse löschen",
				callback: lang.hitch(this, function () {
					this.postCreate();
					var call = this.umcpCommand("asteriskMusic/delete", {
						mohdn: this._mohdn
					});
					call.then(lang.hitch(this, function (data) {
						dialog.notify("Musikklasse wurde entfernt.");

						this._mohSelect.setInitialValue(null, false);
						this._setServer(this._serverdn = this._form.getWidget("server").get("value"));
					}));
				})
			}, {
				type: 'Uploader',
				name: 'upload',
				maxSize: 8129000,
				showClearButton: false,
				onUploaded: lang.hitch(this, function (data) {

					//dialog.alert("upload finished");
					window.setTimeout(lang.hitch(this, function() {
						this._upload._updateLabel();
					}), 0);

					console.debug("Test");
					console.debug(data.filename);
					//console.debug(this._form.getWidget("upload")._uploader);
				

					var call = this.umcpCommand("asteriskMusic/upload", {
						moh: this._form.getWidget("moh").get("value"),
						data: this._upload.value,
						filename: data.filename
					});
					call.then(lang.hitch(this, function (res) {
						if (res.result.error){
							console.debug(res.result.error);
							this._buildErrorPopUp(res.result.error);
						} else {
							dialog.notify("Musikstück wurde hochgeladen.");
							this._setMoh(this._form.getWidget("moh").get("value"));
						}
						this._upload._resetLabel();
					}));
				})
			}];

			var layout = [
				[ "server", "create" ],
				[ "moh", "delete" ],
				[ "upload" ]
			];

			this._form = new Form({
				widgets: widgets,
				layout: layout,
				region: "top"
			});
			this._page.addChild(this._form);
			this.postCreate();
			this._grid = new Grid({
				moduleStore: store("name",
						"asteriskMusic/songs"),
				columns: [{
					name: 'name',
					label: 'Name des Musikstücks'
				}],
				actions: [{
					name: 'delete',
					label: "Löschen",
					callback: lang.hitch(this, function (id) {
						this._grid.filter({
							mohdn: this._mohdn,
							del: id
						});
					})
				}]
			});
			this._page.addChild(this._grid);
			console.log(this);
		},
		postCreate: function () {
			this.inherited(arguments);

			this._serverSelect = this._form.getWidget("server");
			this._serverdn = this._serverdn = this._form.getWidget("server").get("value");
			this._mohSelect = this._form.getWidget("moh");
			this._mohdn = this._mohSelect.get("value");
			this._upload = this._form.getWidget("upload");

			on(this._serverSelect, "onValuesLoaded", lang.hitch(this, function () {
				this._setServer(this._serverdn = this._form.getWidget("server").get("value"));
			}));
			on(this._serverSelect, "onChange", lang.hitch(this, function () {
				this._setServer(this._serverdn = this._form.getWidget("server").get("value"));
			}));

			on(this._mohSelect, "onValuesLoaded", lang.hitch(this, function () {
				this._setMoh(this._mohSelect.get("value"));
			}));
			on(this._mohSelect, "onChange", lang.hitch(this, function () {
				this._setMoh(this._mohSelect.get("value"));
			}));

			on(this._upload._uploader, "onChange", lang.hitch(this, function (data) {
				console.debug(this._form.getWidget("upload").get("value"));
				if (data[0]){
					this._filename = data[0].name;
				}
			}));
		},
		_setServer: function (serverdn) {
			this._serverdn = serverdn;
			this._mohSelect._loadValues({
				"server": this._serverdn
			});
		},
		_setMoh: function (mohdn) {
			this._mohdn = mohdn;
			this._grid.filter({
				mohdn: this._mohdn
			});
		},
		_buildErrorPopUp: function(errorMsg) {
			var container = new ContainerWidget({});
			container.addChild(new Text({
				content: '<pre>'+errorMsg+'</pre>'
			}));

			dialog.alert( container );
		}
	});
});
