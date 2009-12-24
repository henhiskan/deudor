/*!
 * Ext JS Library 3.0.3
 * Copyright(c) 2006-2009 Ext JS, LLC
 * licensing@extjs.com
 * http://www.extjs.com/license
 */
var record;
var store;
var ficha_store;
var procurador_store;
var tribunal_store;
var codigo_store;
var formapago_store;
var reporte_store;

var grid;
var ficha_grid;
var reporte_grid;

var reporte_req;

var tb;
var tabs;
var win;
var nuevo_deudor_btn;
var nuevo_registro_btn;
var deudor_form;
var registro_form;

var reporte_form;
var reporte_win;

Ext.onReady(function(){

  var combo = new Ext.form.ComboBox({
        store: store,
        displayField: 'state',
        typeAhead: true,
        mode: 'local',
        triggerAction: 'all',
        emptyText:'Buscar deudor...',
        selectOnFocus:true,
        width:135
    });


  ////////////////////////////////////////////////////////////
  //////// Action Buttons
  nuevo_deudor_btn = new Ext.Action({
        text: 'Nuevo Deudor',
        handler: function(){
	      win.show();
        },
        iconCls: 'add24',
	tooltip: ' hola',
	scale: 'medium'
    });



  nuevo_registro_btn = new Ext.Action({
	  text: 'Nuevo Registro',
	  handler: function(){
	      registro_win.show();
	  },
	  iconCls: 'add24',
	  tooltip:'hola',
	  scale: 'medium'
      });




  reporte_btn = new Ext.Action({
	  text: 'Reportes',
	  handler: function() {

	      reporte_store.load();
	      tabs.add(reporte_grid);

	      reporte_grid.show();
	      

	      // Ext.Ajax.request({
// 			url : 'getreporte' , 
// 			params : { action : 'getDate' },
// 			method: 'GET',
// 			success: function ( result, request) { 
// 			    //var textArea = Ext.get('log').dom;
// 			    //textArea.value += result.responseText + "\n"; 
// 			Ext.MessageBox.alert('Success', 'Data return from the server: '+ result.responseText); 		
// 			//doJSON(result.responseText);
// 			},
// 			failure: function ( result, request) { 
// 				Ext.MessageBox.alert('Failed', 'Successfully posted form: '+result.date); 
// 			} 
// 		  });
	  },
	  
	  iconCls: 'add24',
	  tooltip:'reporte',
	  scale: 'medium'
      });




////////////////////////////////////////////////////////////

  procurador_store = new Ext.data.Store({
	  proxy: new Ext.data.HttpProxy({
		  url:'/jjdonoso/getprocuradores',
		  method: 'GET'
	      }),
	  reader: new Ext.data.JsonReader({
		  root: 'results',
		  totalProperty: 'total',
		  id: 'pk'
	      },[
  {name: 'nombres', type: 'string', mapping:'fields.nombres'},
  {name: 'apellidos', type: 'string', mapping:'fields.apellidos'},
  {name: 'rut', type: 'string', mapping:'fields.rut'}
		 ])
      });


  codigo_store = new Ext.data.Store({
	  proxy: new Ext.data.HttpProxy({
		  url: '/jjdonoso/getcodigos',
		  method: 'GET'
	      }),
	  reader: new Ext.data.JsonReader({
		  root: 'results',
		  totalProperty: 'total',
		  id: 'pk'
	      },[
  {name: 'codigo', type: 'string', mapping:'fields.codigo_id'},
  {name: 'descripcion', type: 'string', mapping:'fields.descripcion'},
		 ])
      });


  formapago_store = new Ext.data.Store({
	  proxy: new Ext.data.HttpProxy({
		  url: '/jjdonoso/getformapago',
		  method: 'GET'
	      }),
	  reader: new Ext.data.JsonReader({
		  root: 'results',
		  totalProperty: 'total',
		  id: 'pk'
	      },[
  {name: 'codigo', type: 'string', mapping:'fields.codigo'},
  {name: 'nombre', type: 'string', mapping:'fields.nombre'},
		 ])
      });


  tribunal_store = new Ext.data.Store({
	  proxy: new Ext.data.HttpProxy({
		  url: '/jjdonoso/gettribunales',
		  method: 'GET'
	      }),
	  reader: new Ext.data.JsonReader({
		  root: 'results',
		  totalProperty: 'total',
		  id: 'pk'
	      },[
  {name: 'nombre', type: 'string', mapping:'fields.nombre'}
		 ])
      }); 



  reporte_store = new Ext.data.Store({
	  proxy: new Ext.data.HttpProxy({
		  url: '/jjdonoso/getreporte',
		  method: 'GET'
	      }),
	  reader: new Ext.data.JsonReader({
		  root: 'results',
		  totalProperty: 'total',
		  id: 'pk'
	      },[
  {name: 'nombre', type: 'string', mapping:'fields.nombre'}
		 ])
      }); 



  ////////////////////////////////////////

    tb = new Ext.Toolbar();

    tb.add(
	   nuevo_deudor_btn, nuevo_registro_btn, reporte_btn, combo
	);
    
    // create the Data Store
    store = new Ext.data.Store({

	    proxy: new Ext.data.HttpProxy({
		    url: '/jjdonoso/getevento',
		    method: 'GET'
		}),
	    
	    reader: new Ext.data.JsonReader({
		    root: 'results',
		    totalProperty: 'total',
		    id:'pk'
		    
           }, [
    {name: 'fecha', type:'date',dateFormat:'Y-m-d H:i:s',  mapping: 'fields.fecha'},
    {name: 'codigo',type:'string',mapping:'fields.codigo.fields.descripcion'},
    {name: 'descripcion',type:'string',mapping:'fields.descripcion'},
    {name: 'pago',  type:'string',  mapping:'fields.forma_pago'},
    {name: 'abono', type:'int', mapping:'fields.abono_deuda'},
    {name: 'gasto', type:'int', mapping:'fields.gasto_judicial'},
    {name: 'honorario',type:'int',mapping:'fields.honorario'}
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
		    id:'pk'
		    
           }, [
    {name: 'fecha', type:'date',dateFormat:'Y-m-d H:i:s',  mapping: 'fields.fecha_creacion'},
    {name: 'persona',type:'string',mapping:'fields.persona.fields.nombres'},
    {name: 'rut',type:'string',mapping:'fields.persona.fields.rut'},
    {name: 'rol',type:'string',mapping:'fields.rol'},
    {name: 'carpeta',  type:'string',  mapping:'fields.carpeta'},
    {name: 'tribunal', type:'string', mapping:'fields.tribunal.fields.nombre'},
    {name: 'creado_por', type:'string', mapping:'fields.creado_por.fields.persona.fields.nombres'},
    {name: 'deuda_inicial',type:'int',mapping:'fields.deuda_inicial'},
    {name: 'procurador',type:'string',mapping:'fields.procurador.fields.persona.fields.nombres'}
	       ])
	});





    // Grilla con ficha
     grid = new Ext.grid.GridPanel({
	     store: store,
	     height: '200',
	     title: 'Eventos Deudor',

        columns: [
    {header: "Fecha", width: 40, dataIndex: 'fecha', sortable: true,renderer: Ext.util.Format.dateRenderer('d/m/Y')},
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
	     title: 'Deudores',
	     closable:true,
        columns: [
     {header: "Fecha", width: 40, dataIndex: 'fecha', sortable: true, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
   {header: "Persona", width: 20, dataIndex: 'persona', sortable: true},
   {header: "Rut", width: 20, dataIndex: 'rut', sortable: true},
   {header: "Rol", width: 40, dataIndex: 'rol', sortable: true},
   {header: "Carpeta", width: 40, dataIndex: 'carpeta', sortable: true},
   {header: "Tribunal", width: 40, dataIndex: 'tribunal', sortable: true},
   {header: "Creado por", width: 40, dataIndex: 'creado_por', sortable: true},
     {header: "Deuda Inicial", width: 40, dataIndex: 'deuda_inicial', sortable: true},
   {header: "Procurador", width: 40, dataIndex: 'procurador', sortable: true}
        ],
		sm: new Ext.grid.RowSelectionModel({singleSelect: true}),
		viewConfig: {
			forceFit: true
		},
	region: 'center'
	});


     reporte_grid = new Ext.grid.GridPanel({
	     store: reporte_store,
	     height: '200',
	     title: 'Reportes',
	     closable: true,
        columns: [
   {header: "Nombre", width: 50, dataIndex: 'nombre', sortable: true}
        ],
		sm: new Ext.grid.RowSelectionModel({singleSelect: true}),
		viewConfig: {
			forceFit: true
	     },
	region: 'center'
	});


     //////////////////////////////////////////////////
     ////  Tabs  /////


      tabs = new Ext.TabPanel({
        width:450,
        activeTab: 0,
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


////////////////////////////////////////////////////////////
/////////// Formularios ///////////

    reporte_form = new Ext.FormPanel({
	    labelAlign: 'top',
	    frame:true,
	    buttonAlign: 'center',
	    items:[
		   new Ext.form.TextField({
			     fieldLabel: 'Nombre',
			     name: 'nombre',
			     allowBlank:false
		       }),

		new Ext.form.TextArea({
			     fieldLabel: 'Sql',
			     name: 'sql',
			     grow: true,
			     preventScrollbars: true
		    })],
	            buttons: [{
		    text: 'Guardar',
		    handler: function(){
			var f = reporte_form.getForm();
			if (f.isValid()){
			   f.submit({
			     method:'POST',
			     url:'putreporte',
 		             success: function(result, request){
				  Ext.MessageBox.alert('Exitoso', result);
				   }})
			       }
			else{
			    Ext.MessageBox.alert('Errores', 'Por favor, corriga los errores.');
			}
		    }
			
        },{
		    text: 'Cancelar',
		    //handler: function(){registro_win.close();}
		    
        }]
	});
	    



    registro_form = new Ext.FormPanel({
        labelAlign: 'top',
        frame:true,
	buttonAlign: 'center',
        items: [{
            layout:'column',
            items:[{

                layout: 'form',
                items: [
			new Ext.form.DateField({
                        fieldLabel: 'Fecha',
                        name: 'fecha'

			    }),
			new Ext.form.ComboBox({
				hiddenName: 'codigo',
				id:'combo',
				store: codigo_store,
				fieldLabel: 'Codigo',
				displayField: 'descripcion',
				valueField: 'codigo',
				emptyText:'Seleccione un codigo',
				mode: 'local',
				minChars: 0,
				name: 'codigo',
				triggerAction:'all',
				lazyRender:true

			    })
			]
            },{
                layout: 'form',
                items: [
			new Ext.form.ComboBox({
				hiddenName: 'formapago_codigo',
				id:'formapago',
				store: formapago_store,
				fieldLabel: 'Forma pago',
				displayField: 'nombre',
				valueField: 'codigo',
				emptyText:'Seleccione una forma de pago',
				mode: 'local',
				minChars: 0,
				name: 'forma_pago',
				triggerAction:'all'
			    }),
			
                {
                    xtype:'numberfield',
                    fieldLabel: 'Abono Deuda',
                    name: 'abono_deuda'

                }]
	   },{
                layout: 'form',
                items: [{
                    xtype:'numberfield',
                    fieldLabel: 'Gasto Judicial',
                    name: 'gasto_judicial'

                },{
                    xtype:'numberfield',
                    fieldLabel: 'Honorario',
                    name: 'honorario'

                }]
            }]
	     },
		     new Ext.form.TextArea({
			     fieldLabel: 'Descripción',
			     name: 'descripcion',
			     grow: true,
			     preventScrollbars: true
			 })
	    ,{
			 xtype: 'hidden',
			     name: 'rut_deudor'
		     }
	    ],
        buttons: [{
		    text: 'Guardar',
		    handler: function(){
			var f = registro_form.getForm();
			if (f.isValid()){
			   f.submit({
			     method:'POST',
			     url:'putevento',
			     success: function(){
				  Ext.MessageBox.alert('Exitoso', 'Datos enviados');
				   }})
			       }
			else{
			    Ext.MessageBox.alert('Errores', 'Por favor, corriga los errores.');
			}
		    }
			
        },{
		    text: 'Cancelar',
		    //handler: function(){registro_win.close();}
		    
        }]
    });

     ////////////////////////////////////////////////////
     // Nuevo Deudor
     deudor_form = new Ext.FormPanel({
        labelAlign: 'right',
        frame:true,
	buttonAlign: 'center',
	layout: 'column',
	items:[{
	     layout:'form',
	     xtype: 'fieldset',
	     title: 'Datos deudor',
	     items:[

		     new Ext.form.TextField({
			     fieldLabel: 'Rut',
			     name: 'rut',
			     allowBlank:false
			 }),
		     new Ext.form.TextField({
			     fieldLabel: 'Nombres',
			     name: 'nombres',
			     allowBlank:false
			 }),
		     new Ext.form.TextField({
			     fieldLabel: 'Apellidos',
			     name: 'apellidos',
			     allowBlank:false
			 }),
		     new Ext.form.NumberField({
			     fieldLabel: 'Telefono Fijo',
			     name: 'telefono_fijo'
			 }),
		     new Ext.form.NumberField({
			     fieldLabel: 'Telefono movil',
			     name: 'telefono_movil'
			 }),
		     new Ext.form.TextArea({
			     fieldLabel: 'Domicilio',
			     name: 'domicilio',
			     grow: true,
			     preventScrollbars: true
			 })]
		 },{
	      layout:'form',
	      xtype: 'fieldset',
	      title: 'Datos Ficha',
	      items:[

		     new Ext.form.NumberField({
			     fieldLabel: 'Deuda inicial',
			     name: 'deuda_inicial',
			     allowBlank:false
			 }),
		     new Ext.form.DateField({
			     fieldLabel: 'Fecha creacion',
			     name: 'fecha_creacion',
			     allowBlank:false
			 })]

		 },{
	      layout:'form',
	      xtype: 'fieldset',
	      title: 'Datos Juridicos',
	      items:[

		     new Ext.form.ComboBox({
			     hiddenName: 'proc_rut',
			     id:'procurador',
			     store: procurador_store,
			     fieldLabel: 'Procurador',
			     displayField: 'nombres',
			     valueField: 'rut',
			     emptyText: 'Seleccione un procurador',
			     mode:'local',
			     minChars: 0,
			     name: 'procurador',
			     allowBlank: false,
			     triggerAction: 'all'
			 }),

		     new Ext.form.NumberField({
			     fieldLabel: 'Rol',
			     name: 'rol',
			     allowBlank:false
			 }),

		     new Ext.form.ComboBox({
			     hiddenName: 'trib',
			     id:'tribunal',
			     store: tribunal_store,
			     fieldLabel: 'Tribunal',
			     displayField: 'nombre',
			     valueField: 'nombre',
			     emptyText: 'Seleccione un tribunal',
			     mode:'local',
			     minChars: 0,
			     name: 'tribunal',
			     allowBlank: false,
			     triggerAction: 'all'
			 }),

		     new Ext.form.TextField({
			     fieldLabel: 'Carpeta',
			     name: 'carpeta',
			     allowBlank:false
			 })
		     ]
		 }],

	        buttons: [{
		     text: 'Guardar',
		     handler: function(){
			var f = deudor_form.getForm();
			if (f.isValid()){
			   f.submit({
			     method:'POST',
			     url:'putdeudor',
			     success: function(){
				  Ext.MessageBox.alert('Exitoso', 'Datos enviados');
				   }})
			       }
			else{
			    Ext.MessageBox.alert('Errores', 'Por favor, corriga los errores.');
			}
		     }
		 },{
		     text: 'Cancelar',
		     //handler: function(){win.close();}
		 }]
	 });



////////////////////////////////////////////////////////////
//////// ventanas tipo Pop-Up


     win = new Ext.Window({
	     title: 'Nuevo Deudor',
	     width: 800,
	     height: 400,
	     closeAction:'hide',
	     plain:'true',
	     layout: 'fit',
	     items: [deudor_form]
	 });
	     
     registro_win = new Ext.Window({
	     title: 'Nuevo Registro',
	     width: 600,
	     height: 300,
	     closeAction:'hide',
	     plain:'true',
	     layout: 'fit',
	     items: [ registro_form]
	 });


     reporte_win = new Ext.Window({
	     title: 'Nuevo Reporte',
	     width: 600,
	     height: 300,
	     closeAction:'hide',
	     plain:'true',
	     layout: 'fit',
	     items: [ reporte_form]
	 });

////////////////////////////////////////
//////// AjaX Functions
////////////////////////////////////////



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
		title: 'Sistema de Deuda JJDonoso',
		width: 840,
		height: 600,
		layout: 'border',
		tbar: tb,
		items: [
			tabs
			
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
	    });

	ficha_grid.getSelectionModel().on('rowselect', function(sm, rowIdx, r) {
		//var detailPanel = Ext.getCmp('detailPanel');
		//bookTpl.overwrite(detailPanel.body, r.data);
		grid.enable();
		nuevo_registro_btn.enable();
		store.load({params:{rut:r.data.rut}});
		grid.show();

		// Agregar rut de deudor en formulario de 
		// nuevo registro
		registro_form.getForm().findField('rut_deudor').setValue(r.data.rut);

	    });

   reporte_grid.on('rowdblclick', function(grid, rowIdx, e) {
	   record= grid.getStore().getAt(rowIdx);

	   if (!Ext.fly('frmDummy')) {
                      var frm = document.createElement('form');
                      frm.id = 'frmDummy';
                      frm.name = id;
                      frm.className = 'x-hidden';
                      document.body.appendChild(frm);
                  }
	   

	   Ext.Ajax.request({
		   url : 'getreporte' , 
		   params : { nombre : record.data.nombre },
		   method: 'POST',
	           form: Ext.fly('frmDummy'),
		   isUpload: true,
		   success: function ( result, request) { 

		       Ext.MessageBox.alert('Success', 'Data return from the server: '+ result.responseText);
	     
	},
			failure: function ( result, request) { 
	    Ext.MessageBox.alert('Failed', 'Error : '+result.responseText); 
		   }
	       });


	    });

	
  grid.disable();
  nuevo_registro_btn.disable();
  ficha_store.load();
  codigo_store.load();
  formapago_store.load();
  procurador_store.load();
  tribunal_store.load();
  
});