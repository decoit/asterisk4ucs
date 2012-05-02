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

	i18nClass: "umc.modules.asteriskMusic",

	buildRendering: function () {
		this.inherited(arguments);

		this._page = new umc.widgets.Page({
			headerText: "Hallo Welt!",
			helpText: "Hallo, du digitalisierte Welt!",
		});
		this.addChild(this._page);

		this._content = new umc.widgets.ExpandingTitlePane({
			title: "Fubar",
		});
		this._page.addChild(this._content);

		var widgets = [{
			type: 'ComboBox',
			name: 'moh',
			label: "Musikklasse",
			dynamicValues: "asteriskMusic/queryMohs",
		}, {
			type: 'Button',
			name: 'create',
			label: "Musikklasse anlegen",
//			defaultButton: true,
			callback: function () {
				alert("anlegen");
			},
		}, {
			type: 'Button',
			name: 'delete',
			label: "Musikklasse löschen",
			callback: function () {
				alert("entfernen");
			},
		}, {
			type: 'Button',
			name: 'upload',
			label: "Musikstück hinzufügen",
			callback: function () {
				alert("upload");
			},
		}];

		var layout = [
			[ "moh", "create" ],
			[ "delete", "upload" ],
		];

		this._form = new umc.widgets.Form({
			widgets: widgets,
			layout: layout,
			region: "top",
		});
		this._content.addChild(this._form);

		var self = this;
		dojo.connect(this._form.getWidget("moh"),
					"onValuesLoaded", function () {
			self.setMoh(this.getValue());
		});
		dojo.connect(this._form.getWidget("moh"),
					"onChange", function () {
			self.setMoh(this.getValue());
		});

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
		this._content.addChild(this._grid);

		console.log(this);
		fubar = this;
	},
	setMoh: function (mohdn) {
		this._mohdn = mohdn;
		this._grid.filter({
			mohdn: this._mohdn,
		});
	},
});

