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

dojo.provide("umc.modules.asteriskUser");

dojo.require("umc.widgets.Module");
dojo.require("umc.widgets.ContainerWidget");
dojo.require("umc.widgets.Page");
dojo.require("umc.widgets.Form");
dojo.require("umc.widgets.Grid");

dojo.declare("umc.modules.asteriskUser", [ umc.widgets.Module ], {
	_buttons: null,

	_forms: [],

	buildRendering: function () {
		this.inherited(arguments);

		this._buttons = [{
			name: 'submit',
			label: "Speichern",
			callback: dojo.hitch(this, function () {
				this.save();
			}),
		}];

		var tabContainer = new umc.widgets.TabContainer({
			nested: true,
		});
		this.addChild(tabContainer);

		tabContainer.addChild(this.renderPhones());

		tabContainer.addChild(this.renderMailbox());

		// forwarding is not yet implemented
		//tabContainer.addChild(this.renderForwarding());

		this.startup();
		this.load();
	},
	renderMailbox: function () {
		var page = new umc.widgets.Page({
			title: "Anrufbeantworter",
			headerText: "Anrufbeantwortereinstellungen",
			footerButtons: this._buttons,
			closable: false,
		});

		var container = new umc.widgets.ContainerWidget({
			scrollable: true,
		});
		page.addChild(container);

		var noMailboxHint = new umc.widgets.Text({
			content: "Leider hat Ihnen der Administrator keinen " +
				"Anrufbeantworter zugewiesen.",
			region: "top",
		});
		container.addChild(noMailboxHint);
		this._mailboxHint = noMailboxHint;

		var widgets = [{
			type: 'TextBox',
			name: 'mailbox/password',
			label: "PIN-Nummer zum Abrufen",
		}, {
			type: 'ComboBox',
			name: 'mailbox/email',
			label: "Per eMail benachrichtigen?",
			staticValues: [
				{ id: '0', label: "Nein" },
				{ id: '1', label: "Ja, gerne!" },
			],
		}, {
			type: 'ComboBox',
			name: 'mailbox/timeout',
			label: "Mailbox antwortet nach",
			staticValues: [
				{ id:   '5', label: "5 Sekunden" },
				{ id:  '10', label: "10 Sekunden" },
				{ id:  '20', label: "20 Sekunden" },
				{ id:  '30', label: "30 Sekunden" },
				{ id:  '45', label: "45 Sekunden" },
				{ id:  '60', label: "einer Minute" },
				{ id: '120', label: "zwei Minuten" },
				{ id: '180', label: "π Minuten" },
			],
		}];

		var layout = [
			'mailbox/password',
			'mailbox/email',
			'mailbox/timeout'
		];

		var form = new umc.widgets.Form({
			widgets: widgets,
			layout: layout,
			scrollable: true,
		});
		container.addChild(form);
		this._forms.push(form);
		this._mailboxForm = form;

		this._mailboxForm.domNode.style.display = 'none';
		this._mailboxHint.domNode.style.display = 'block';

		return page;
	},
	renderPhones: function () {
		var page = new umc.widgets.Page({
			title: "Telefone",
			headerText: "Telefoneinstellungen",
			footerButtons: this._buttons,
			closable: false,
		});

		var container = new umc.widgets.ExpandingTitlePane({
			title: "Klingelreihenfolge",
		});
		page.addChild(container);

		var grid = new umc.widgets.Grid({
			moduleStore: umc.store.getModuleStore("extension",
				"asteriskUser/phones"),
			query: {
				filter:'*'
			},
			columns: [{
				name: 'name',
				label: "Telefon",
				editable: false,
			}],
			actions: [{
				name: 'earlier',
				label: "Früher",
				canExecute: dojo.hitch(this, function (values) {
					return true;
				}),
				callback: dojo.hitch(this, function (id) {
					alert("frueher" + id);
				}),
			}, {
				name: 'later',
				label: "Später",
				canExecute: dojo.hitch(this, function (values) {
					return true;
				}),
				callback: dojo.hitch(this, function (id) {
					alert("spaeter" + id);
				}),
			}],
		});
		container.addChild(grid);

		var widgets = [{
			type: 'ComboBox',
			name: 'phones/interval',
			label: "Klingelintervall",
			staticValues: [
				{ id:   '2', label:  "2 Sekunden" },
				{ id:   '4', label:  "4 Sekunden" },
				{ id:   '6', label:  "6 Sekunden" },
				{ id:   '8', label:  "8 Sekunden" },
				{ id:  '10', label: "10 Sekunden" },
			],
		}];

		var layout = [
			'phones/interval',
		];

		var form = new umc.widgets.Form({
			region: 'top',
			widgets: widgets,
			layout: layout,
			scrollable: true,
		});
		page.addChild(form);
		this._forms.push(form);

		page.startup();
		return page;
	},
	renderForwarding: function () {
		var page = new umc.widgets.Page({
			title: "Weiterleitung",
			headerText: "Weiterleitungseinstellungen",
			footerButtons: this._buttons,
			closable: false,
		});

		var container = new umc.widgets.ContainerWidget({
			scrollable: true,
		});
		page.addChild(container);

		var widgets = [{
			type: 'TextBox',
			name: 'forwarding/number',
			label: "Weiterleitungsziel",
		}];

		var layout = [
			'forwarding/number'
		];

		var form = new umc.widgets.Form({
			widgets: widgets,
			layout: layout,
			scrollable: true,
		});
		container.addChild(form);
		this._forms.push(form);

		return page;
	},
	setValues: function (values) {
		dojo.forEach(this._forms, function (form) {
			form.setFormValues(values);
		}, this);

		// disable the mailbox form if needed
		if (values.mailbox) {
			this._mailboxForm.domNode.style.display = 'block';
			this._mailboxHint.domNode.style.display = 'none';
		} else {
			this._mailboxForm.domNode.style.display = 'none';
			this._mailboxHint.domNode.style.display = 'block';
		}
	},
	getValues: function () {
		var values = {};
		dojo.forEach(this._forms, function (form) {
			dojo.mixin(values, form.gatherFormValues());
		}, this);
		return values;
	},
	load: function () {
		this.umcpCommand('asteriskUser/load').then(
			dojo.hitch(this, function (data) {
				this.setValues(data.result);
			}),
			dojo.hitch(this, function () {
				// hm...
			})
		);
	},
	save: function () {
		var data = this.getValues();
		this.umcpCommand('asteriskUser/save', data);
	},
});

