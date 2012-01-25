
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

		console.log(this);
	},
});

