/*!
 * Ext JS Library 3.0.3
 * Copyright(c) 2006-2009 Ext JS, LLC
 * licensing@extjs.com
 * http://www.extjs.com/license
 */

var store;
var ficha_store;
var grid;
var tb;
var ficha_tab;
Ext.onReady(function(){

  var combo = new Ext.form.ComboBox({
        store: store,
        displayField: 'state',
        typeAhead: true,
        mode: 'local',
        triggerAction: 'all',
        emptyText:'Buscar cliente...',
        selectOnFocus:true,
        width:135
    });


    tb = new Ext.Toolbar();

    tb.add(
	   {	
        iconCls: 'add24',
		   scale: 'medium',
		   text: 'nuevo cliente',
        tooltip: '<b>Quick Tips</b><br/>Icon only button with tooltip'
		   }, combo
	);
    
    // create the Data Store
    store = new Ext.data.Store({

	    proxy: new Ext.data.HttpProxy({
		    url: '/jjdonoso/getdata',
		    method: 'GET'
		}),
	    
	    reader: new Ext.data.JsonReader({
		    root: 'results',
		    totalProperty: 'total',
		    id:'fecha'
		    
           }, [
    {name: 'fecha', type:'date',dateFormat:'Y/m/d',  mapping: 'fecha'},
    {name: 'codigo',type:'string',mapping:'codigo'},
    {name: 'descripcion',type:'string',mapping:'descripcion'},
    {name: 'pago',  type:'string',  mapping:'pago'},
    {name: 'abono', type:'int', mapping:'abono'},
    {name: 'gasto', type:'int', mapping:'gasto'},
    {name: 'honorario',type:'int',mapping:'honorario'}
	       ])
	});



    ficha_store = new Ext.data.Store({
	    proxy: new Ext.data.HttpProxy({
		    url: '/jjdonoso/getficha',
		    method: 'GET'
		}),
	    
	    reader: new Ext.data.JsonReader({
		    root: 'results',
		    totalProperty: 'total',
		    id:'fecha'
		    
           }, [
    {name: 'fecha', type:'date',dateFormat:'Y/m/d',  mapping: 'fecha'},
    {name: 'persona',type:'string',mapping:'persona'},
    {name: 'rol',type:'string',mapping:'rol'},
    {name: 'carpeta',  type:'string',  mapping:'carpeta'},
    {name: 'tribunal', type:'int', mapping:'tribunal'},
    {name: 'creado_por', type:'int', mapping:'creado_por'},
    {name: 'deuda_inicial',type:'int',mapping:'deuda_inicial'},
    {name: 'procurador',type:'string',mapping:'procurador'}
	       ])
	});





    // create the grid
     grid = new Ext.grid.GridPanel({
	     store: store,
	     height: '200',
        columns: [
            {header: "Fecha", width: 40, dataIndex: 'fecha', sortable: true},
            {header: "Codigo", width: 20, dataIndex: 'codigo', sortable: true},
            {header: "Descripción", width: 40, dataIndex: 'descripcion', sortable: true},
    {header: "Forma Pago", width: 40, dataIndex: 'pago', sortable: true},
    {header: "Abono", width: 40, dataIndex: 'abono', sortable: true},
    {header: "Honorario", width: 40, dataIndex: 'honorario', sortable: true},
    {header: "Gasto", width: 40, dataIndex: 'gasto', sortable: true}
	    
        ],
		sm: new Ext.grid.RowSelectionModel({singleSelect: true}),
		viewConfig: {
			forceFit: true
	     },
	      region: 'center'
	});


     ficha_grid = new Ext.grid.GridPanel({
	     store: ficha_store,
	     height: '200',
        columns: [
   {header: "Fecha", width: 40, dataIndex: 'fecha', sortable: true},
   {header: "Persona", width: 20, dataIndex: 'persona', sortable: true},
   {header: "Rol", width: 40, dataIndex: 'rol', sortable: true},
   {header: "Carpeta", width: 40, dataIndex: 'carpeta', sortable: true},
   {header: "Tribunal", width: 40, dataIndex: 'tribunal', sortable: true},
   {header: "Creado por", width: 40, dataIndex: 'creado_por', sortable: true},
     {header: "Deuda Inicial", width: 40, dataIndex: 'deuda', sortable: true},
   {header: "Procurador", width: 40, dataIndex: 'procurador', sortable: true}
        ],
		sm: new Ext.grid.RowSelectionModel({singleSelect: true}),
		viewConfig: {
			forceFit: true
		},
	region: 'center'
	});
     //////////////////////////////////////////////////
     ////  Tabs  /////


      ficha_tab = new Ext.TabPanel({
        width:450,
        activeTab: 1,
        frame:true,
	region:'center',
        items:[
	       ficha_grid,
	       grid 
        ]
    });





     var search = new Ext.FormPanel({
	     frame: true,
	     title: "Busqueda de Registro",
	     region: 'west',
	     width: '250',
	     align: 'top',
	     items: [{xtype: 'textfield',
		      fieldLabel: 'busqueda',
		      name: 'Busqueda'
		 }],
	     buttons: [{
		     text: 'Buscar'
		 }]
	 });

     var formulario = new Ext.FormPanel({
        labelAlign: 'top',
        frame:true,
        title: 'Nuevo registro',
        bodyStyle:'padding:5px 5px 0',
        width: 300,
	height: 150,
	region: 'south',
        items: [{
            layout:'column',
            items:[{
                columnWidth:.2,
                layout: 'form',
                items: [
			new Ext.form.DateField({
                        fieldLabel: 'Fecha',
                        name: 'fecha',
                        width:100,
                        allowBlank:false
			    }),
                {
                    xtype:'textfield',
                    fieldLabel: 'Codigo',
                    name: 'codigo',
                    anchor:'95%'
                }]
            },{
                columnWidth:.2,
                layout: 'form',
                items: [{
                    xtype:'textfield',
                    fieldLabel: 'Forma Pago',
                    name: 'pago',
                    anchor:'95%'
                },{
                    xtype:'textfield',
                    fieldLabel: 'Abono Deuda',
                    name: 'abono',
                    anchor:'95%'
                }]
	   },{
                columnWidth:.2,
                layout: 'form',
                items: [{
                    xtype:'textfield',
                    fieldLabel: 'Gasto Judicial',
                    name: 'gasto',
                    anchor:'95%'
                },{
                    xtype:'textfield',
                    fieldLabel: 'Honorario',
                    name: 'honorario',
                    anchor:'95%'
                }]
            }]
	     },{

		    xtype:'textfield',
                    fieldLabel: 'Descripcion',
                    name: 'desc',
                    anchor:'75%'
	     }],

        buttons: [{
            text: 'Guardar'
        },{
            text: 'Cancelar'
        }]
    });




////////////////////////////////////////////////////////////
//////////////// PANEL PRINCIPAL ////////////////////


	// define a template to use for the detail view
	var bookTplMarkup = [
		'Nombre: {nombre}<br/>',
		'Rut: {Rut}<br/>',
		'Deuda: {Deuda}<br/>',
		'Abono: {Abono}<br/>'
	];
	var bookTpl = new Ext.Template(bookTplMarkup);

	var ct = new Ext.Panel({
		renderTo: 'areadata',
		frame: true,
		title: 'Ficha',
		width: 840,
		height: 600,
		layout: 'border',
		//tbar: tb,
		items: [
			ficha_tab,
			tb
			//			{
			//	id: 'detailPanel',
			//	region: 'east',
			//	width: 200,
			//	bodyStyle: {
			//		background: '#ffffff',
			//		padding: '47px'
			//	},
			//	html: '.'
			//}
		]
	})
	grid.getSelectionModel().on('rowselect', function(sm, rowIdx, r) {
		var detailPanel = Ext.getCmp('detailPanel');
		bookTpl.overwrite(detailPanel.body, r.data);
	});
    store.load();
});