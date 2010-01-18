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
var usuario_store;
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
var search;

var ficha_ajax;



{% load tags %}


Ext.onReady(function(){

  Ext.QuickTips.init();
  // turn on validation errors beside the field globally
  Ext.form.Field.prototype.msgTarget = 'side';

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
	tooltip: ' Agregar los datos de un nuevo deudor',
	scale: 'medium'
    });



  nuevo_registro_btn = new Ext.Action({
	  text: 'Nuevo Registro',
	  handler: function(){
	      registro_win.show();
	  },
	  iconCls: 'registro',
	  tooltip:'Agregar un nuevo registro a un deudor',
	  scale: 'medium'
      });




  reporte_btn = new Ext.Action({
	  text: 'Reportes',
	  handler: function() {
	      reporte_store.load();	      
	      if (tabs.getItem('reportes') == null)
		  {
		      tabs.add(reporte_grid);
		      reporte_grid.show();
		  }
	      else{
		  tabs.unhideTabStripItem('reportes');
	      }
	      
	  },
	  
	  iconCls: 'reporte',
	  tooltip:'reporte',
	  scale: 'medium'
      });




///////////////////////////////////////////
//////////// STORES          //////////////


  ficha_store = new Ext.data.Store({
	  proxy: new Ext.data.HttpProxy({
		  url: '/deudor/getficha',
		  method: 'GET'
	      }),
	    
	  reader: new Ext.data.JsonReader({
		  root: 'results',
		  totalProperty: 'total',
		  id:'pk'
		    
	      }, [
  {name: 'fecha', type:'date',dateFormat:'Y-m-d H:i:s',  mapping: 'fields.fecha_creacion'},
  {name: 'nombres',type:'string',mapping:'fields.persona.fields.nombres'},
  {name: 'apellidos',type:'string',mapping:'fields.persona.fields.apellidos'},
  {name: 'rut',type:'string',mapping:'fields.persona.pk'},
  {name: 'rol',type:'string',mapping:'fields.rol'},
  {name: 'carpeta',  type:'string',  mapping:'fields.carpeta'},
  {name: 'tribunal', type:'string', mapping:'fields.tribunal', convert: function(v) {return v ? v.fields.nombre : null;}},
  {name: 'creado_por', type:'string', mapping:'extras.getNombreCreador' },
  {name: 'deuda_inicial',type:'int',mapping:'fields.deuda_inicial'},
  {name: 'procurador',type:'string',mapping:'extras.getNombreProcurador' }
		  ])
      });


  evento_store = new Ext.data.Store({
	  
	  proxy: new Ext.data.HttpProxy({
		  url: '/deudor/getevento',
		  method: 'GET'
	      }),
	    
	  reader: new Ext.data.JsonReader({
		  root: 'results',
		  totalProperty: 'total',
		  id:'pk'
		  
           }, [
  {name: 'fecha', type:'date',dateFormat:'Y-m-d H:i:s',  mapping: 'fields.fecha'},
  {name: 'prox_pago', type:'date',dateFormat:'Y-m-d H:i:s',  mapping: 'fields.proximo_pago'},
  {name: 'codigo',type:'string',mapping:'fields.codigo.fields.descripcion'},
  {name: 'descripcion',type:'string',mapping:'fields.descripcion'},
  {name: 'pago',  type:'string',  mapping:'fields.forma_pago',convert: function(v) {return v ? v.fields.nombre : null;}},
  {name: 'abono', type:'int', mapping:'fields.abono_deuda'},
  {name: 'gasto', type:'int', mapping:'fields.gasto_judicial'},
  {name: 'honorario',type:'int',mapping:'fields.honorario'}
	       ])
      });




  procurador_store = new Ext.data.Store({
	  proxy: new Ext.data.HttpProxy({
		  url:'/deudor/getprocuradores',
		  method: 'GET'
	      }),
	  reader: new Ext.data.JsonReader({
		  root: 'results',
		  totalProperty: 'total',
		  id: 'pk'
	      },[
  {name: 'nombres', type: 'string', mapping:'fields.nombres'},
  {name: 'apellidos', type: 'string', mapping:'fields.apellidos'},
  {name: 'nombre', type:'string', mapping:'extras.short_name'},
  {name: 'rut', type: 'string', mapping:'pk'}
		 ])
      });

  usuario_store = new Ext.data.Store({
	  proxy: new Ext.data.HttpProxy({
		  url:'/deudor/getusuarios',
		  method: 'GET'
	      }),
	  reader: new Ext.data.JsonReader({
		  root: 'results',
		  totalProperty: 'total',
		  id: 'pk'
	      },[
  {name: 'nombre', type: 'string', mapping:'extras.short_name'},
  {name: 'rut', type: 'string', mapping:'pk'}
		 ])
      });



  codigo_store = new Ext.data.Store({
	  proxy: new Ext.data.HttpProxy({
		  url: '/deudor/getcodigos',
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
		  url: '/deudor/getformapago',
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
		  url: '/deudor/gettribunales',
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
		  url: '/deudor/getreporte',
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



    ///////////////////////////////////
    //           GRIDS
    ///////////////////////////////////

    // Deudores
    ficha_grid = new Ext.grid.EditorGridPanel({
	    store: ficha_store,
	    height: '200',
	    title: 'Deudores',
	    clicksToEdit: 1,

	    columns: [
  {header: "Fecha", width: 30, dataIndex: 'fecha', sortable: true, 
   renderer: Ext.util.Format.dateRenderer('d/m/Y')},

  {header: "Nombres", width: 40, dataIndex: 'nombres', sortable: true
   {% ifnotequal  usuario|getTipoUsuario "procurador" %}
   ,editor: new Ext.form.TextField({
	     allowBlank: true
	 })
   {% endifnotequal %}
    },
  {header: "Apellidos", width: 40, dataIndex: 'apellidos', sortable: true
   {% ifnotequal  usuario|getTipoUsuario "procurador" %}
   ,editor: new Ext.form.TextField({
	     allowBlank: true
       })
       {% endifnotequal %}
},
  {header: "Rut", width: 25, dataIndex: 'rut', sortable: true},
  {header: "Rol", width: 30, dataIndex: 'rol', sortable: true
   {% ifnotequal  usuario|getTipoUsuario "procurador" %}
   ,editor: new Ext.form.NumberField({
	   allowBlank: true,
	   allowNegative: false
       })
       {% endifnotequal %}
  },
    {header: "Carpeta", width: 40, dataIndex: 'carpeta', sortable: true
   {% ifnotequal  usuario|getTipoUsuario "procurador" %}
     ,editor: new Ext.form.TextField({
	     allowBlank: true
	 })
       {% endifnotequal %}
    },
    {header: "Tribunal", 
     width: 50, 
     dataIndex: 'tribunal', 
     sortable: true
   {% ifnotequal  usuario|getTipoUsuario "procurador" %}
     ,editor: new Ext.form.ComboBox({
                    typeAhead: true,
                    triggerAction: 'all',
                    lazyRender: true,
		    store: tribunal_store,
		    displayField: 'nombre',
		    valueField: 'nombre'
                })
   {% endifnotequal %}
    },
  {header: "Creado por", width: 40, dataIndex: 'creado_por', sortable: true
   {% ifnotequal  usuario|getTipoUsuario "procurador" %}
      ,editor: new Ext.form.ComboBox({
                    typeAhead: true,
                    triggerAction: 'all',
                    lazyRender: true,
		    store: usuario_store,
		    displayField: 'nombre',
		    valueField: 'rut'
                })
   {% endifnotequal %}
  },
    {header: "Deuda Inicial", width: 40, dataIndex: 'deuda_inicial', sortable: true},
  {header: "Procurador", width: 40, dataIndex: 'procurador', sortable: true

   {% ifnotequal  usuario|getTipoUsuario "procurador" %}
   , editor: new Ext.form.ComboBox({
                    typeAhead: true,
                    triggerAction: 'all',
                    lazyRender: true,
		    store: procurador_store,
		    displayField: 'nombre',
		    valueField: 'rut'
                })
   {% endifnotequal %}
  }

   {% ifnotequal  usuario|getTipoUsuario "procurador" %}
    ,{width: 40, dataIndex: 0, id: 'deleter', sortable: false, fixed: true,
     renderer: function(v, p, record, rowIndex){
        return '<div class="deleter" style="width: 15px; height: 16px;"></div>';
	 }}
  {% endifnotequal %}
     ],
		sm: new Ext.grid.RowSelectionModel({singleSelect: true}),
		viewConfig: {
			forceFit: true
		},
	region: 'center'
	    
	});

    {% ifnotequal  usuario|getTipoUsuario "procurador" %}
    ficha_grid.on('cellclick', function(grilla, rowIndex, columnIndex, e){
	    
	    if(columnIndex == ficha_grid.getColumnModel().getIndexById('deleter')) {
		
		var record= ficha_grid.getStore().getAt(rowIndex);
		
		Ext.MessageBox.confirm('Confirm', '¿Esta seguro de querer eliminar esta ficha y sus eventos?', function(btn){
		     respuesta = btn;
		     if (respuesta == 'yes'){
			    Ext.Ajax.request({
				params : {id: record.id},
			        url : 'deleteficha' , 
				method: 'GET',
	                        form: Ext.fly('frmDummy'),
		   isUpload: true,
		   success: function ( result, request) { 
			ficha_grid.getStore().remove(record);
			ficha_grid.getView().refresh();
			   },
		   failure: function ( result, request) { 
		          Ext.MessageBox.alert('Failed', 'Error : '+result.responseText); 
		            }
			});

			
		     }
		 });

		
	       
	     }
	});
    {% endifnotequal %}

    ficha_grid.on('afterEdit', function(e) {

	    Ext.Ajax.request({
		    params : { campo : e.field,
			    valor:  e.value,
			    id: e.record.id},
		   url : 'putficha' , 
		   method: 'POST',
	           form: Ext.fly('frmDummy'),
		   isUpload: true,
		   success: function ( result, request) { 
			e.record.commit();
			ficha_store.load();
	     
		    },
		   failure: function ( result, request) { 
			Ext.MessageBox.alert('Failed', 'Error : '+result.responseText); 
		    }
		});
	    
	    
	});


    // Eventos deudor
     grid = new Ext.grid.EditorGridPanel({
	     store: evento_store,
	     height: '200',
	     title: 'Eventos Deudor',
	     clicksToEdit: 1,

        columns: [
    {header: "Fecha", width: 40, dataIndex: 'fecha', sortable: true,
     renderer: Ext.util.Format.dateRenderer('d/m/Y')},

    {header: "Proximo Pago", width: 40, dataIndex: 'prox_pago', sortable: true, 
     renderer: Ext.util.Format.dateRenderer('d/m/Y')},

    {header: "Codigo", width: 60, dataIndex: 'codigo', sortable: true
   {% ifnotequal  usuario|getTipoUsuario "procurador" %}
     , editor: new Ext.form.ComboBox({
                    typeAhead: true,
                    triggerAction: 'all',
                    lazyRender: true,
		    store: codigo_store,
		    displayField: 'descripcion',
		    valueField: 'codigo'
	 })
	 {% endifnotequal %}
    },
    {header: "Descripción", width: 70, dataIndex: 'descripcion', sortable: true
   {% ifnotequal  usuario|getTipoUsuario "procurador" %}
     ,editor: new Ext.form.TextField({
	     allowBlank: true}
	 )
   {% endifnotequal %}
    },
    {header: "Forma Pago", width: 40, 
     dataIndex: 'pago', sortable: true
   {% ifnotequal  usuario|getTipoUsuario "procurador" %}
     ,editor: new Ext.form.ComboBox({
                    typeAhead: true,
                    triggerAction: 'all',
                    lazyRender: true,
		    store: formapago_store,
		    displayField: 'nombre',
		    valueField: 'codigo'

	 })
   {% endifnotequal %}
    },

    {header: "Abono", width: 40, dataIndex: 'abono', sortable: true
   {% ifnotequal  usuario|getTipoUsuario "procurador" %}
   , editor: new Ext.form.NumberField({
	     allowBlank: true,
	     allowNegative: false
       })
   {% endifnotequal %}
    },
    {header: "Honorario", width: 40, dataIndex: 'honorario', sortable: true
   {% ifnotequal  usuario|getTipoUsuario "procurador" %}
   , editor: new Ext.form.NumberField({
	     allowBlank: true,
	     allowNegative: false
       })

   {% endifnotequal %}
    },
    {header: "Gasto", width: 40, dataIndex: 'gasto', sortable: true
   {% ifnotequal  usuario|getTipoUsuario "procurador" %}
     ,editor: new Ext.form.NumberField({
	     allowBlank: true,
	     allowNegative: false
	 })
   {% endifnotequal %}
    }
   {% ifnotequal  usuario|getTipoUsuario "procurador" %}
   ,{width: 40, dataIndex: 0, id: 'deleter', sortable: false, fixed: true,
     renderer: function(v, p, record, rowIndex){
        return '<div class="deleter" style="width: 15px; height: 16px;"></div>';
       }}
    {% endifnotequal %}
        ],
		sm: new Ext.grid.RowSelectionModel({singleSelect: true}),
		viewConfig: {
			forceFit: true
	     },
	      region: 'center'
	});


     {% ifnotequal  usuario|getTipoUsuario "procurador" %}
     grid.on('cellclick', function(grid, rowIndex, columnIndex, e){
	     
         if(columnIndex==grid.getColumnModel().getIndexById('deleter')) {
	     var record= grid.getStore().getAt(rowIndex);
	     
	     var record = grid.getStore().getAt(rowIndex);
	     var respuesta = "";
	     Ext.MessageBox.confirm('Confirm', '¿Esta seguro de querer eliminar este evento?', function(btn){
		     respuesta = btn;
		     if (respuesta == 'yes'){
			    Ext.Ajax.request({
				params : {id: record.id},
			        url : 'deleteevento' , 
				method: 'GET',
	                        form: Ext.fly('frmDummy'),
		   isUpload: true,
		   success: function ( result, request) { 
			grid.getStore().remove(record);
		        grid.getView().refresh();
			   },
		   failure: function ( result, request) { 
		          Ext.MessageBox.alert('Failed', 'Error : '+result.responseText); 
		            }
			});

			
		     }
		 });

	     }
	 });

     {% endifnotequal %}
     
     grid.on('afterEdit', function(e) {
	     
	    Ext.Ajax.request({
		    params : {
			campo : e.field,
			valor: e.value,
			id: e.record.id,
			    rut_deudor: registro_form.getForm().findField('rut_deudor').value},
		   url : 'puteventoedit' , 
		   method: 'POST',
	           form: Ext.fly('frmDummy'),
		   isUpload: true,
		   success: function ( result, request) { 
			e.record.commit();
			//refresh para ocultar los id en combobox
			evento_store.load();
		    },
			failure: function ( result, request) { 
			Ext.MessageBox.alert('Failed', 'Error : '+result.responseText); 
		    }
		});
	    
	 });





     reporte_grid = new Ext.grid.GridPanel({
	     id: 'reportes',
	     store: reporte_store,
	     height: '200',
	     title: 'Reportes',
        columns: [
   {header: "Nombre", width: 50, dataIndex: 'nombre', sortable: true}
        ],
		sm: new Ext.grid.RowSelectionModel({singleSelect: true}),
		viewConfig: {
			forceFit: true
	     },
	region: 'center'
	});


////////////////////////////
////  Tabs  ///////////////


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
     // en cada cambio de Tab, cambio el datastore
     // del buscador para el filtro
     tabs.on('tabchange', function(){

	     search.store = tabs.activeTab.store;
	 }); 


///////////////////////////////////////
///// SEARCH Toolbar     

     search = new Ext.ux.form.SearchField({
	     store: ficha_store,
	     width:320
	 });

     tb = new Ext.Toolbar();

     tb.add(
	    {% ifnotequal  usuario|getTipoUsuario "procurador" %}
	    nuevo_deudor_btn,
	    {% endifnotequal %} nuevo_registro_btn, reporte_btn,
	    'Busqueda: ',' ',
	    search, '    ',
	    {
                text:'Logout',
                handler:function(){
                    Ext.Ajax.request({
                        url:'/deudor/logout',
                        success:function(){window.location='/deudor/login';},
                        failure:function(){window.location='/deudor/ficha';},
                    });
                },
		    }
	    );
    
    
///////////////////////////////////
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
		    handler: function(){win.hide();}
		    
        }]
	});
	    

    
    // formulario de ingreso de un Evento
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
                        name: 'fecha',
			format: 'd/m/Y',
			value: (new Date()).format('d/m/Y')
			    }),

			new Ext.form.DateField({
				fieldLabel: 'Fecha Proximo Pago',
				name: 'proximo_pago',
				format: 'd/m/Y'
				//value: (new Date()).format('d/m/Y')
			    }),
			
			new Ext.form.ComboBox({
				hiddenName: 'codigo',
				id:'combo',
				store: codigo_store,
				allowBlank: false,
				fieldLabel: 'Codigo',
				displayField: 'codigo',
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
				allowBlank: true,
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
			allowBlank: true,
			name: 'abono_deuda'

                }]
	   },{
                layout: 'form',
                items: [{
                    xtype:'numberfield',
                    fieldLabel: 'Gasto Judicial',
		    allowBlank: true,
                    name: 'gasto_judicial'

                },{
                    xtype:'numberfield',
                    fieldLabel: 'Honorario',
		    allowBlank: true,
                    name: 'honorario'

                }]
            }]
	     },
		     new Ext.form.TextArea({
			     fieldLabel: 'Descripción',
			     name: 'descripcion',
			     grow: true,
			     width: 180,
			     allowBlank: false,
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
					Ext.MessageBox.alert('Exitoso', 'Evento guardado');
					registro_form.getForm().reset();
					registro_win.hide();
					evento_store.load();
					ficha_store.load();
				    }})
			       }
			else{
			    Ext.MessageBox.alert('Errores', 'Por favor, corriga los errores.');
			}
		    }
			
        },{
		    text: 'Cancelar',
		    handler: function(){registro_win.hide();}
		    
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
	     width: 340,
	     items:[
    		{
		    fieldLabel: 'Rut',
		    name: 'rut',
		    xtype: 'textfield',
		    vtype: 'Rut',
		    allowBlank: true,
		    maskRe: new RegExp ('[0-9kK]'),
		    enableKeyEvents: true,
		    listeners: {
			'keyup': function(field, e) {
			    var rut =
			    field.getValue().replace(/[.-]/g,'').split('').reverse();
			    if (rut.length>0){
				var rut_array=[rut[0],'-'];
				var cont=0;
				for(i=1;i<rut.length;i++){
				    if (cont==3){
					rut_array.push('.');
					cont=0;
				    }
				    rut_array.push(rut[i]);
				    cont++;
				}
				this.setValue(rut_array.reverse().join(''));
			    }}
		    }// end listeners
    
		},
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
			width: 155,
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
			     allowBlank:false,
			     format: 'd/m/Y',
			     value: (new Date()).format('d/m/Y')
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
			     allowBlank: true,
			     triggerAction: 'all'
			 }),

		     new Ext.form.NumberField({
			     fieldLabel: 'Rol',
			     name: 'rol',
			     allowBlank: true
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
			     allowBlank: true,
			     triggerAction: 'all'
			 }),

		     new Ext.form.TextField({
			     fieldLabel: 'Carpeta',
			     name: 'carpeta',
			     allowBlank: true
			 })
		     ]
		 }],

	        buttons: [{
		     text: 'Guardar',
		     handler: function(){
			var f = deudor_form.getForm();
			if (f.isValid()){

			    //chequear si existe un deudor con 
			    // el rut ingresado
			    rut = deudor_form.getForm().findField('rut').value.split('-')[0].replace(/\./g,'');
			    if (ficha_store.find('rut',rut) == -1){

				f.submit({
					method:'POST',
					url:'putdeudor',
					success: function(form, action){
					    
					    Ext.MessageBox.alert('Exitoso', 'Datos guardados');
					    deudor_form.getForm().reset();
					    win.hide();
					    ficha_store.load();
					},
					failure: function(form, action){
					    Ext.Msg.alert('error', action.result.descripcion);
					}
				    })

				    }
			    else {

				Ext.MessageBox.alert("Error", 
						     "El rut ingresado pertenece a un deudor registrado");
			    }
			}
			else{
			    Ext.MessageBox.alert('Errores', 'Por favor, corriga los errores.');
			}
		     }
		 },{
		     text: 'Cancelar',
		     handler: function(){win.hide();}
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
		title: 'Sistema de Deuda',
		width: 840,
		height: 600,
		layout: 'border',
		tbar: tb,
		items: [
			tabs
			
		]
	    });
	


	// sm, rowIdx, r
	ficha_grid.on('rowdblclick', function(grid_selected, rowIdx, e) {
		
		record= grid_selected.getStore().getAt(rowIdx);

		grid.enable();

		nuevo_registro_btn.enable();
		evento_store.baseParams = {rut: record.data.rut};
		evento_store.load();
		grid.show();

		// Agregar rut de deudor en formulario de 
		// nuevo registro
		registro_form.getForm().findField('rut_deudor').setValue(record.data.rut);

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
  usuario_store.load();
});