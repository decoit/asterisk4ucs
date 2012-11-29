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
   "umc/widgets/ContainerWidget",
   "umc/widgets/Page",
   "umc/widgets/Form",
   "umc/widgets/Grid",
   "umc/widgets/ExpandingTitlePane",
   "umc/widgets/Text",
   "umc/store",
   "umc/i18n!umc/modules/asteriskUser"
],
function(declare,store,lang,array,Text,TabbedModule,ContainerWidget,Page,Form,Grid,ExpandingTitlePane){
   return declare("umc.modules.asteriskUser",[ TabbedModule ],{
      _buttons: null,
      _mailboxHint: null,
      _mailboxForm: null,
      _grid: null,
      _forms: [],


      buildRendering: function () {
         this.inherited(arguments);

         this._buttons = [{
            name: 'submit',
            label: "Speichern",
            callback: lang.hitch(this, function () {
               this.save();
            })
         }];

         this._forms = [];

                  

         this.addChild(this.renderPhones());

         this.addChild(this.renderMailbox());

         this.addChild(this.renderForwarding());

         //this.startup();
         this.load();
      },
      renderMailbox: function () {
         var page = new Page({
            title: "Anrufbeantworter",
            headerText: "Anrufbeantwortereinstellungen",
            footerButtons: this._buttons,
            closable: false
         });

         
	    
         var widgets = [{
            type: 'TextBox',
            name: 'mailbox/password',
            label: "PIN-Nummer zum Abrufen"
         }, {
            type: 'ComboBox',
            name: 'mailbox/email',
            label: "Per eMail benachrichtigen?",
            staticValues: [
               { id: '0', label: "Nein" },
               { id: '1', label: "Ja, gerne!" }
            ]
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
               { id: '180', label: "π Minuten" }
            ]
         }];
		
	    var container = new ContainerWidget({
            scrollable: true
         });
         page.addChild(container);

         var noMailboxHint = new Text({
            content: "Leider hat Ihnen der Administrator keinen " +
               "Anrufbeantworter zugewiesen.",
            region: "top"
         });
         container.addChild(noMailboxHint);
         this._mailboxHint = noMailboxHint;
         var layout = [
            'mailbox/password',
            'mailbox/email',
            'mailbox/timeout'
         ];

         var form = new Form({
            widgets: widgets,
            layout: layout,
            scrollable: true
         });
         container.addChild(form);
         this._forms.push(form);
         this._mailboxForm = form;

         this._mailboxForm.domNode.style.display = 'none';
         this._mailboxHint.domNode.style.display = 'block';

         return page;
      },
      renderPhones: function () {
         var page = new Page({
            title: "Telefone",
            headerText: "Telefoneinstellungen",
            footerButtons: this._buttons,
            closable: false
         });

         var container = new ExpandingTitlePane({
            title: "Klingelreihenfolge"
         });
         page.addChild(container);

         this._grid = new Grid({
            moduleStore: store("dn",
               "asteriskUser/phones"),
            query: {
               filter:'*'
            },
            columns: [{
               name: 'position',
               label: "Position",
               editable: false,
               hidden: true
            }, {
               name: 'name',
               label: "Telefon",
               editable: false
            }],
            actions: [{
               name: 'earlier',
               label: "Früher",
               isStandardAction: true,
               canExecute: lang.hitch(this, function (values) {
                  return values.position > 0;
               }),
               callback: lang.hitch(this, function (id) {
                  this._grid.filter({
                     dn: id,
                     position: -1
                  });
               })
            }, {
               name: 'later',
               label: "Später",
               isStandardAction: true,
               canExecute: lang.hitch(this, function (values) {
                  return (values.position + 1 <
                     this._grid._grid.rowCount);
               }),
               callback: lang.hitch(this, function (id) {
                  this._grid.filter({
                     dn: id,
                     position: 1
                  });
               })
            }]
         });
         container.addChild(this._grid);


         this._grid._grid.canSort = function (index) {
            return false;
         };

         var widgets = [{
            type: 'ComboBox',
            name: 'phones/interval',
            label: "Klingelintervall",
            staticValues: [
               { id:   '2', label:  "2 Sekunden" },
               { id:   '4', label:  "4 Sekunden" },
               { id:   '6', label:  "6 Sekunden" },
               { id:   '8', label:  "8 Sekunden" },
               { id:  '10', label: "10 Sekunden" }
            ]
         }];

         var layout = [
            'phones/interval'
         ];

         var form = new Form({
            region: 'top',
            widgets: widgets,
            layout: layout,
            scrollable: true
         });
         page.addChild(form);
         this._forms.push(form);

         //page.startup();
         return page;
      },
      renderForwarding: function () {
         var page = new Page({
            title: "Weiterleitung",
            headerText: "Weiterleitungseinstellungen",
            footerButtons: this._buttons,
            closable: false
         });

         var container = new ContainerWidget({
            scrollable: true
         });
         page.addChild(container);

         var widgets = [{
            type: 'TextBox',
            name: 'forwarding/number',
            label: "Weiterleitungsziel"
         }];

         var layout = [
            'forwarding/number'
         ];

         var form = new Form({
            widgets: widgets,
            layout: layout,
            scrollable: true
         });
         container.addChild(form);
         this._forms.push(form);

         return page;
      },
      setValues: function (values) {
         array.forEach(this._forms, function (form) {
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
         array.forEach(this._forms, function (form) {
            lang.mixin(values, form.gatherFormValues());
         }, this);
         return values;
      },
      load: function () {
	    this.standby(true);
         this.umcpCommand('asteriskUser/load').then(
            lang.hitch(this, function (data) {
			this.standby(false);
               this.setValues(data.result);
            }),
            lang.hitch(this, function () {
               // hm...
			this.standby(false);
            })
         );
      },
      save: function () {
	    this.standby(true);
         var data = this.getValues();
         this.umcpCommand('asteriskUser/save', data).then(
		   lang.hitch(this, function() {
			this.standby(false);
	    }),
		   lang.hitch(this, function() {
			this.standby(false);
	    }));
      }
   });
});
