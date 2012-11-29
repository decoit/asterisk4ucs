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
	"umc/dialog/notify",
	"umc/widgets/Text",
	"umc/dialog/alert",
	"dojo/on",
	"umc/i18n!umc/modules/asteriskMusic"
],
function(declare,lang,array,TabbedModule,Module,ContainerWidget,Page,Form,Grid,ExpandingTitlePane,store,notify,Text,alert,on,_){
	return declare("umc.modules.asteriskMusic",[TabbedModule],{
		_page: null,
		_form: null,
		_serverSelect: null,
		_serverdn: null,
		_mohSelect: null,
		_mohdn: null,
		_upload: null,
		_filename: null,

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
					var name = prompt("Bitte geben Sie den Namen für die neue Musikklasse ein:");
					if (!name) {
						alert("Ungültiger Name.");
						return;
					}

					var call = this.umcpCommand("asteriskMusic/create", {
						name: name,
						server: this._serverdn
					});
					call.then(lang.hitch(this, function (data) {
						notify("Musikklasse wurde angelegt.");

						this._mohSelect.setInitialValue(data.result.newDn, false);
						this._setServer(this._serverdn);
					}));
				})
			}, {
				type: 'Button',
				name: 'delete',
				label: "Musikklasse löschen",
				callback: lang.hitch(this, function () {
					var call = this.umcpCommand("asteriskMusic/delete", {
						mohdn: this._mohdn
					});
					call.then(lang.hitch(this, function (data) {
						notify("Musikklasse wurde entfernt.");

						this._mohSelect.setInitialValue(null, false);
						this._setServer(this._serverdn);
					}));
				})
			}, {
				type: 'Uploader',
				name: 'upload',
				maxSize: 8129000,
				showClearButton: false,
				onUploaded: lang.hitch(this, function () {
					//alert("upload finished");
					window.setTimeout(lang.hitch(this, function() {
						this._upload._updateLabel();
					}), 0);
					var call = this.umcpCommand("asteriskMusic/upload", {
						moh: this._mohdn,
						data: this._upload.value,
						filename: this._filename
					});
					call.then(lang.hitch(this, function (res) {
						if (res.result.error){
							this._buildErrorPopUp(res.result.error);
						} else {
							notify("Musikstück wurde hochgeladen.");
							this._setMoh(this._mohdn);
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
			this._serverdn = this._serverSelect.getValue();
			this._mohSelect = this._form.getWidget("moh");
			this._mohdn = this._mohSelect.getValue();
			this._upload = this._form.getWidget("upload");

			on(this._serverSelect, "onValuesLoaded", lang.hitch(this, function () {
				this._setServer(this._serverSelect.getValue());
			}));
			on(this._serverSelect, "onChange", lang.hitch(this, function () {
				this._setServer(this._serverSelect.getValue());
			}));

			on(this._mohSelect, "onValuesLoaded", lang.hitch(this, function () {
				this._setMoh(this._mohSelect.getValue());
			}));
			on(this._mohSelect, "onChange", lang.hitch(this, function () {
				this._setMoh(this._mohSelect.getValue());
			}));

			on(this._upload._uploader, "onChange", lang.hitch(this, function (data) {
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
		
			alert( container );
		}
	});
});

