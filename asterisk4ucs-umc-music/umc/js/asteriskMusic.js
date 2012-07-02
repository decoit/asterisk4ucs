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

dojo.provide("umc.modules.asteriskMusic");

dojo.require("umc.widgets.Module");

dojo.declare("umc.modules.asteriskMusic", [ umc.widgets.Module ], {
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

		this._page = new umc.widgets.Page({
			headerText: "Warteschlangenmusikverwaltungstool",
		});
		this.addChild(this._page);

		var widgets = [{
			type: 'ComboBox',
			name: 'server',
			label: "Server",
			dynamicValues: "asteriskMusic/queryServers",
		}, {
			type: 'ComboBox',
			name: 'moh',
			label: "Musikklasse",
			dynamicValues: "asteriskMusic/queryMohs",
			dynamicOptions: function (values) {
				return { serverdn: values.server };
			},
			depends: [
				"server",
			],
		}, {
			type: 'Button',
			name: 'create',
			label: "Musikklasse anlegen",
			callback: dojo.hitch(this, function () {
				var name = prompt("Bitte geben Sie den Namen für die neue Musikklasse ein:");
				if (!name) {
					alert("Ungültiger Name.");
					return;
				}

				var call = this.umcpCommand("asteriskMusic/create", {
					name: name,
					server: this._serverdn,
				});
				call.then(dojo.hitch(this, function (data) {
					umc.dialog.notify("Musikklasse wurde angelegt.");

					this._mohSelect.setInitialValue(data.result.newDn, false);
					this._setServer(this._serverdn);
				}));
			}),
		}, {
			type: 'Button',
			name: 'delete',
			label: "Musikklasse löschen",
			callback: dojo.hitch(this, function () {
				var call = this.umcpCommand("asteriskMusic/delete", {
					mohdn: this._mohdn,
				});
				call.then(dojo.hitch(this, function (data) {
					umc.dialog.notify("Musikklasse wurde entfernt.");

					this._mohSelect.setInitialValue(null, false);
					this._setServer(this._serverdn);
				}));
			}),
		}, {
			type: 'Uploader',
			name: 'upload',
			maxSize: 8129000,
			showClearButton: false,
			onUploaded: dojo.hitch(this, function () {
				//alert("upload finished");
				window.setTimeout(dojo.hitch(this, function() {
					this._upload._updateLabel();
				}), 0);
				var call = this.umcpCommand("asteriskMusic/upload", {
					moh: this._mohdn,
					data: this._upload.value,
					filename: this._filename,
				});
				call.then(dojo.hitch(this, function (res) {
					if (res.result.error){
						this._buildErrorPopUp(res.result.error);
					} else {
						umc.dialog.notify("Musikstück wurde hochgeladen.");
						this._setMoh(this._mohdn);
					}
					this._upload._resetLabel();
				}));
			}),
		}];

		var layout = [
			[ "server", "create" ],
			[ "moh", "delete" ],
			[ "upload" ],
		];

		this._form = new umc.widgets.Form({
			widgets: widgets,
			layout: layout,
			region: "top",
		});
		this._page.addChild(this._form);

		this._grid = new umc.widgets.Grid({
			moduleStore: umc.store.getModuleStore("name",
					"asteriskMusic/songs"),
			columns: [{
				name: 'name',
				label: 'Name des Musikstücks',
			}],
			actions: [{
				name: 'delete',
				label: "Löschen",
				callback: dojo.hitch(this, function (id) {
					this._grid.filter({
						mohdn: this._mohdn,
						delete: id,
					});
				}),
			}],
		});
		this._page.addChild(this._grid);

		console.log(this);
		fubar = this;
	},
	postCreate: function () {
		this.inherited(arguments);

		this._serverSelect = this._form.getWidget("server");
		this._serverdn = this._serverSelect.getValue();
		this._mohSelect = this._form.getWidget("moh");
		this._mohdn = this._mohSelect.getValue();
		this._upload = this._form.getWidget("upload");

		dojo.connect(this._serverSelect, "onValuesLoaded", dojo.hitch(this, function () {
			this._setServer(this._serverSelect.getValue());
		}));
		dojo.connect(this._serverSelect, "onChange", dojo.hitch(this, function () {
			this._setServer(this._serverSelect.getValue());
		}));

		dojo.connect(this._mohSelect, "onValuesLoaded", dojo.hitch(this, function () {
			this._setMoh(this._mohSelect.getValue());
		}));
		dojo.connect(this._mohSelect, "onChange", dojo.hitch(this, function () {
			this._setMoh(this._mohSelect.getValue());
		}));

		dojo.connect(this._upload._uploader, "onChange", dojo.hitch(this, function (data) {
			if (data[0])
				this._filename = data[0].name;
		}));
	},
	_setServer: function (serverdn) {
		this._serverdn = serverdn;
		this._mohSelect._loadValues({
			"server": this._serverdn,
		});
	},
	_setMoh: function (mohdn) {
		this._mohdn = mohdn;
		this._grid.filter({
			mohdn: this._mohdn,
		});
	},
	_buildErrorPopUp: function(errorMsg) {
		var container = new umc.widgets.ContainerWidget({});
		container.addChild(new umc.widgets.Text({
			content: '<pre>'+errorMsg+'</pre>',
		}));
		
		umc.dialog.alert( container );
	},
});

