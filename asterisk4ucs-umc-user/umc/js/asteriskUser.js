
dojo.provide("umc.modules.asteriskUser");

dojo.require("umc.widgets.Module");
dojo.require("umc.widgets.ContainerWidget");
dojo.require("umc.widgets.Page");
dojo.require("umc.widgets.Form");
dojo.require("umc.widgets.Grid");

dojo.declare("umc.modules.asteriskUser", [ umc.widgets.Module ], {
	buildRendering: function () {
		this.inherited(arguments);

		var tabContainer = new umc.widgets.TabContainer({
			nested: true,
		});
		this.addChild(tabContainer);

		tabContainer.addChild(this.renderMailbox());
		tabContainer.addChild(this.renderPhones());
		tabContainer.addChild(this.renderForwarding());
	},
	renderMailbox: function () {
		var page = new umc.widgets.Page({
			title: "Anrufbeantworter",
			headerText: "Anrufbeantwortereinstellungen",
			closable: false,
		});

		var container = new umc.widgets.ContainerWidget({
			scrollable: true,
		});
		page.addChild(container);

		var widgets = [{
			type: 'TextBox',
			name: 'mailbox/pin',
			label: "Abruf-Pin",
		}, {
			type: 'ComboBox',
			name: 'mailbox/email',
			label: "Per eMail benachrichtigen?",
			staticValues: [
				{ id: 'false', label: "Nein" },
				{ id:  'true', label: "Ja, gerne!" },
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
			'mailbox/pin',
			'mailbox/email',
			'mailbox/timeout'
		];

		var form = new umc.widgets.Form({
			widgets: widgets,
			layout: layout,
			scrollable: true,
		});
		page.addChild(form);

		return page;
	},
	renderPhones: function () {
		var page = new umc.widgets.Page({
			title: "Telefone",
			headerText: "Telefoneinstellungen",
			closable: false,
		});

		var container = new umc.widgets.ContainerWidget({
			scrollable: true,
		});
		page.addChild(container);

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
		}, {
			type: 'Grid',
			name: 'phones/sequence',
			label: "Klingelreihenfolge",
			moduleStore: umc.store.getModuleStore("extension",
				"asteriskUser/phones"),
			query: {'*':'*'},
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
		}];

		var layout = [
			'phones/interval',
			'phones/sequence',
		];

		var form = new umc.widgets.Form({
			widgets: widgets,
			layout: layout,
			scrollable: true,
		});
		page.addChild(form);

		return page;
	},
	renderForwarding: function () {
		var page = new umc.widgets.Page({
			title: "Weiterleitung",
			headerText: "Weiterleitungseinstellungen",
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
		page.addChild(form);

		return page;
	},
});

