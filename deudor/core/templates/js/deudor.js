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
var receptor_store;
var reporte_store;

var grid;
var ficha_grid;
var reporte_grid;

var reporte_req;

var tb;
var tabs;
var preview;
var win;
var nuevo_deudor_btn;
var nuevo_registro_btn;
var deudor_form;
var registro_form;

var reporte_form;
var reporte_win;
var search;

var ficha_ajax;
var summary;


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
		    nom =  ficha_grid.getSelectionModel().getSelected().data.nombres;
		    apell= ficha_grid.getSelectionModel().getSelected().data.apellidos;
		    rut =  ficha_grid.getSelectionModel().getSelected().data.rut;
		    registro_win.setTitle("Rut:" + rut+
					  " Deudor :"+ nom + ' ' + apell);
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



	imprimir_btn = new Ext.Action({
		text: 'Imprimir',
		handler: function(){

		    if (!Ext.fly('frmDummyprint')) {
			var frm = document.createElement('form');
			frm.id = 'frmDummyprint';
			frm.name = id;
			frm.className = 'x-hidden';
			document.body.appendChild(frm);
		    }
	   

		    Ext.Ajax.request({
			    //url:'/deudor/printFicha?ficha_id=' + ficha_grid.getSelectionModel().getSelected().id,
			    url:'/deudor/printFicha?rut_deudor=' + ficha_grid.getSelectionModel().getSelected().data.rut,
			    method: 'GET',
			    form: Ext.fly('frmDummyprint'),
			    isUpload: true,
			    success:function( result, request){
				Ext.MessageBox.alert("Enviado");
			    },
			    failure: function ( result, request) { 
				Ext.MessageBox.alert('Error', result.responseText); 
			    }
			});

		},
		//iconCls: 'imprimir',
		tooltip:'Impresión de Ficha',
		scale: 'medium'
	    });


	///////////////////////////////////////////
	//////////// STORES          //////////////

	// SortData Overload
	Ext.override(Ext.data.Store, {
		sortData : function(f, direction){
		    direction = direction || 'ASC';
		    var st = this.fields.get(f).sortType;
		    var fn = function(r1, r2){
			var v1 = st(r1.data[f], r1), v2 = st(r2.data[f], r2);
			return v1 > v2 ? 1 : (v1 < v2 ? -1 : 0);
		    };
		    this.data.sort(direction, fn);
		    if(this.snapshot && this.snapshot != this.data){
			this.snapshot.sort(direction, fn);
		    }
		}
	    });

	ficha_store = new Ext.data.Store({
		proxy: new Ext.data.HttpProxy({
			url: '/deudor/getficha',
			method: 'GET'
		    }),
		remoteSort: true,	    
		reader: new Ext.data.JsonReader({
			root: 'results',
			totalProperty: 'total',
			id:'pk'
		    
		    }, [
	{name: 'fecha', type:'date',dateFormat:'Y-m-d H:i:s',  mapping: 'fields.fecha_creacion'},
	{name: 'nombres',type:'string',mapping:'fields.persona.fields.nombres'},
	{name: 'apellidos',type:'string',mapping:'fields.persona.fields.apellidos'},
	{name: 'rut',type:'string',mapping:'fields.persona.pk'},
	{name: 'rut_verif',type:'string',mapping:'extras.getRutDeudor'},
	{name: 'rol',type:'string',mapping:'fields.rol'},
	{name: 'domicilio',type:'string',mapping:'fields.persona.fields.domicilio'},
	{name: 'telefono_fijo',type:'string',mapping:'fields.persona.fields.telefono_fijo'},
	{name: 'telefono_oficina',type:'string',mapping:'fields.persona.fields.telefono_oficina'},
	{name: 'telefono_movil',type:'string',mapping:'fields.persona.fields.telefono_movil'},

	{name: 'carpeta',  type:'string',  mapping:'fields.carpeta'},
	{name: 'tribunal', type:'string', mapping:'fields.tribunal', convert: function(v) {return v ? v.fields.nombre : null;}},
	{name: 'creado_por', type:'string', mapping:'extras.getNombreCreador' },
	{name: 'deuda_inicial',type:'int',mapping:'fields.deuda_inicial'},
	{name: 'procurador_name',type:'string',mapping:'extras.getNombreProcurador'},
	{name: 'procurador',type:'string',mapping:'extras.getIdProcurador'},
	{name: 'sistema_origen',type:'string',mapping:'fields.sistema_origen' }
			])
	    });


	evento_store = new Ext.data.GroupingStore({
	  
		proxy: new Ext.data.HttpProxy({
			url: '/deudor/getevento',
			method: 'GET'
		    }),
		groupField: 'ficha',
		sortInfo: {field: 'fecha',direction: 'ASC'},
		reader: new Ext.data.JsonReader({
			root: 'results',
			totalProperty: 'total',
			id:'pk'
		  
		    }, [
	{name: 'fecha', 
	 type:'date',
	 dateFormat:'Y-m-d H:i:s',  
	 mapping: 'fields.fecha', 
	 sortType:  function(v, r){
		fecha = r.get('fecha');
		orden = r.get('orden');
		return  (fecha!=''?fecha.dateFormat('YmdHi'):'') + orden;
	    }
	},
	{name: 'orden', type:'int',  mapping: 'fields.orden'},
	{name: 'prox_pago', type:'date',dateFormat:'Y-m-d H:i:s',  mapping: 'fields.proximo_pago'},
	{name: 'codigo',type:'string',mapping:'fields.codigo.fields.descripcion'},
	{name: 'descripcion',type:'string',mapping:'fields.descripcion'},
	{name: 'receptor',  type:'string',  mapping:'fields.receptor',convert: function(v) {return v ? v.fields.nombre : null;}},
	{name: 'pago',  type:'string',  mapping:'fields.forma_pago',convert: function(v) {return v ? v.fields.nombre : null;}},
	{name: 'capital', type:'int', mapping:'fields.capital'},
	{name: 'gasto', type:'int', mapping:'fields.gasto_judicial'},
	{name: 'honorario',type:'int',mapping:'fields.honorario'},
	{name: 'costas',type:'int',mapping:'fields.costas'},
	{name: 'interes',type:'int',mapping:'fields.interes'},
	{name: 'ficha',type:'int',mapping:'fields.ficha'}
  
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
	{name: 'codigo', type: 'string', mapping:'pk'},
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
	{name: 'nombre', type: 'string', mapping:'fields.nombre'}
		       ])
	    });

	receptor_store = new Ext.data.Store({
		proxy: new Ext.data.HttpProxy({
			url: '/deudor/getreceptor',
			method: 'GET'
		    }),
		reader: new Ext.data.JsonReader({
			root: 'results',
			totalProperty: 'total',
			id: 'pk'
		    },[
	{name: 'nombre', type: 'string', mapping:'fields.nombre'},
	{name: 'id', type: 'int', mapping:'pk'}
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
	{name: 'nombre', type: 'string', mapping:'fields.nombre'},
	{name: 'id', type: 'int', mapping:'pk'}
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


	sist_orig_store = new Ext.data.Store({
		proxy: new Ext.data.HttpProxy({
			url: '/deudor/getsistorig',
			method: 'GET'
		    }),
		reader: new Ext.data.JsonReader({
			root: 'results',
			totalProperty: 'total',
			id: 'pk'
		    },[
	{name: 'nombre', type: 'string', mapping:'fields.nombre'},
	{name: 'id', type: 'int', mapping:'pk'}
		       ])
	    }); 


	///////////////////////////////////
	//           GRIDS
	///////////////////////////////////

	// Deudores
	ficha_grid = new Ext.grid.EditorGridPanel({
		store: ficha_store,
		width: 400,
		height: '200',
		title: 'Deudores',
		clicksToEdit: 1,


		columns: [
	{header: "Fecha", width: 45, dataIndex: 'fecha', sortable: true, 
	 renderer: Ext.util.Format.dateRenderer('d/m/Y')},

	{header: "Nombres", width: 40, dataIndex: 'nombres', sortable: true},
	{header: "Apellidos", width: 40, dataIndex: 'apellidos', sortable: true},
	{header: "Rut", width: 25, dataIndex: 'rut_verif', sortable: true},
	{header: "Deuda Inicial", width: 40, dataIndex: 'deuda_inicial', sortable: true},

	{header: "Tribunal", 
	 width: 50, 
	 dataIndex: 'tribunal', 
	 sortable: true
	},
	{header: "Rol", width: 30, dataIndex: 'rol', sortable: true}, 
	{header: "Carpeta", width: 40, dataIndex: 'carpeta', sortable: true},
	{header: "Procurador", width: 40, dataIndex: 'procurador_name', sortable: true},
	{header: "ProcuradorId", width: 40, dataIndex: 'procurador', hidden:true}
	//{% ifnotequal  usuario|getTipoUsuario "procurador" %}
	,{width: 40, dataIndex: 0, id: 'deleter', sortable: false, fixed: true,
	  renderer: function(v, p, record, rowIndex){
		return '<div class="deleter" style="width: 15px; height: 16px;"></div>';
	    }}
	//{% endifnotequal %}
			  ],
		sm: new Ext.grid.RowSelectionModel({singleSelect: true}),
		viewConfig: {
		    forceFit: true
		},
		region: 'center',
	    
		// paging bar on the bottom
		bbar: new Ext.PagingToolbar({
			pageSize: 25,
			store: ficha_store,
			displayInfo: true,
			displayMsg: 'Fichas desplegadas {0} - {1} de {2}',
			emptyMsg: "Sin fichas para mostar",

		    })

	    });

	//{% ifnotequal  usuario|getTipoUsuario "procurador" %}
	ficha_grid.on('cellclick', function(grilla, rowIndex, columnIndex, e){

		var record= ficha_grid.getStore().getAt(rowIndex);	    
		Ext.getCmp("preview").getForm().loadRecord(record);

		if(columnIndex == ficha_grid.getColumnModel().getIndexById('deleter')) {
		
		
		    Ext.MessageBox.confirm('Confirm',
					   '¿Esta seguro de querer eliminar esta ficha y sus eventos?',
					   function(btn){
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
							       Ext.MessageBox.alert('Error', result.responseText); 
							   }
						       });

			
					       }
					   });
		}


		evento_store.baseParams = {rut: record.data.rut};
		evento_store.load();

		// Agregar rut de deudor en formulario de 
		// nuevo registro
		registro_form.getForm().findField('rut_deudor').setValue(record.data.rut);
		Ext.getCmp("preview").getForm().loadRecord(record);

		// Activar el boton de imprimir
		imprimir_btn.enable();

	    });
	//{% endifnotequal %}

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
			    Ext.MessageBox.alert('Error', result.responseText); 
			}
		    });
	    
	    
	    });


	// Eventos deudor

	// define a custom summary function

	// utilize custom extension for Group Summary
	summary = new Ext.ux.grid.GroupSummary();


	grid = new Ext.grid.EditorGridPanel({
		store: evento_store,
		height: '200',
		title: 'Registros',
		clicksToEdit: 1,

		columns: [
	{header: "Fecha", 
	 width: 75,
	 dataIndex: 'fecha', 
	 sortable: true,
	 renderer: Ext.util.Format.dateRenderer('d/m/Y'),
	 editor: new Ext.form.DateField({
		 format: 'd/m/Y'
	     })

	},{
	    header: 'Ficha',
	    width: 20,
	    sortable: true,
	    dataIndex: 'ficha',
	    renderer: function(v, params, record){
		rut = registro_form.getForm().findField('rut_deudor').value;
		return "Registros de Persona Rut:" + rut;
	    },
	},

	{
	    header: "#", 
	    width: 20, 
	    dataIndex: 'orden', 
	    sortable: true,
	    editor: new Ext.form.NumberField({
		    allowBlank: true,
		    allowNegative: false,
		    allowDecimals: false
		})
	}

	,

	{header: "Proximo Pago", 
	 width: 40,
	 dataIndex: 'prox_pago',
	 sortable: true, 
	 renderer: Ext.util.Format.dateRenderer('d/m/Y')
	 //{% ifnotequal  usuario|getTipoUsuario "procurador" %}
	 ,editor: new Ext.form.DateField({
		 format: 'd/m/Y'
	     })
	 //{% endifnotequal %}
	},

	{header: "Codigo", 
	 width: 60,
	 dataIndex: 'codigo', 
	 sortable: true,
	 editor: new Ext.form.ComboBox({
		 typeAhead: true,
		 triggerAction: 'all',
		 lazyRender: true,
		 store: codigo_store,
		 displayField: 'descripcion',
		 valueField: 'codigo'
	     })
	},
	{header: "Descripción",
	 width: 90,
	 dataIndex: 'descripcion', 
	 sortable: true,
	 editor: new Ext.form.TextArea({
		 allowBlank: true}
	     )
	},
	{header: "Receptor",
	 dataIndex: 'receptor', 
	 sortable: true,
	 width: 50,
	 editor: new Ext.form.ComboBox({
		 typeAhead: true,
		 triggerAction: 'all',
		 lazyRender: true,
		 store: receptor_store,
		 displayField: 'nombre',
		 valueField: 'id'
	     })
	},

	{header: "Forma Pago", width: 70, 
	 dataIndex: 'pago', sortable: true
     
	 //{% ifnotequal  usuario|getTipoUsuario "procurador" %}
	 ,editor: new Ext.form.ComboBox({
		 typeAhead: true,
		 triggerAction: 'all',
		 lazyRender: true,
		 store: formapago_store,
		 displayField: 'nombre',
		 valueField: 'codigo'

	     })
	 //{% endifnotequal %}
	},

	{header: "Capital", width: 40, 
	 dataIndex: 'capital', 
	 sortable: true,
	 summaryType: 'sum',
	 summaryRenderer: function(v, params, data){
		return '$' + v ;
	    }

	 //{% ifnotequal  usuario|getTipoUsuario "procurador" %}
	 , editor: new Ext.form.NumberField({
		 allowBlank: true,
		 allowNegative: false,
		 allowDecimals: false
	     })
	 //{% endifnotequal %}
	},
	{header: "Honorario", width: 40, 
	 dataIndex: 'honorario', 
	 sortable: true,
	 summaryType: 'sum',
	 summaryRenderer: function(v, params, data){
		return '$' + v ;
	    }

	 //{% ifnotequal  usuario|getTipoUsuario "procurador" %}
	 , editor: new Ext.form.NumberField({
		 allowBlank: true,
		 allowNegative: false,
		 allowDecimals: false
	     })

	 //{% endifnotequal %}
	},

    
	{header: "Costas", width: 40,
	 dataIndex: 'costas', 
	 sortable: true,
	 summaryType: 'sum',
	 summaryRenderer: function(v, params, data){
		return '$' + v ;
	    }

	 //{% ifnotequal  usuario|getTipoUsuario "procurador" %}
	 ,editor: new Ext.form.NumberField({
		 allowBlank: true,
		 allowNegative: false,
		 allowDecimals: false
	     })
	 //{% endifnotequal %}
	},
	{header: "Interes", width: 40,
	 dataIndex: 'interes', 
	 sortable: true ,
	 summaryType: 'sum',
	 summaryRenderer: function(v, params, data){
		return '$' + v ;
	    }
	 //{% ifnotequal  usuario|getTipoUsuario "procurador" %}
	 ,editor: new Ext.form.NumberField({
		 allowBlank: true,
		 allowNegative: false,
		 allowDecimals: false
	     })
	 //{% endifnotequal %}
	},
	{header: "Total", width: 40, 
	 dataIndex: 'total', 
	 summaryType: 'sum',
	 renderer: function(v, params, record){
		return '$ ' + ( (record.data.capital==''?0:parseInt(record.data.capital)) +
				(record.data.honorario==''?0:parseInt(record.data.honorario)) +
				(record.data.costas==''?0:parseInt(record.data.costas)) +
				(record.data.interes==''?0:parseInt(record.data.interes)));
	    },

	 sortable: true }

	,{header: "Gasto Jud", width: 40, 
	  id: 'gasto',
	  dataIndex: 'gasto', 
	  sortable: true,
	  summaryType: 'sum',
	  summaryRenderer: function(v, params, data){
		return '$' + v ;
	    }

	  ,editor: new Ext.form.NumberField({
		  allowBlank: true,
		  allowNegative: false,
		  allowDecimals: false
	      })
	}

	,{width: 40, dataIndex: 0, id: 'deleter', sortable: false, fixed: true,
	  renderer: function(v, p, record, rowIndex){
		return '<div class="deleter" style="width: 15px; height: 16px;"></div>';
	    }}
			  ],
		sm: new Ext.grid.RowSelectionModel({singleSelect: true}),
		viewConfig: {
		    forceFit: true
		},
		region: 'center',

		view: new Ext.grid.GroupingView({
			forceFit: true,
			showGroupName: false,
			enableNoGroups: false,
			enableGroupingMenu: false,
			hideGroupedColumn: true
		    }),

		plugins: summary,
	     
	    });


	grid.on('cellclick', function(grid, rowIndex, columnIndex, e){


		if(columnIndex==grid.getColumnModel().getIndexById('deleter')) {
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
					    Ext.MessageBox.alert('Error', result.responseText); 
					}
				    });

			
			    }
			});

		}
	    });
     
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
			    Ext.MessageBox.alert('Error', result.responseText); 
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
		width:350,
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
	       //{% ifnotequal  usuario|getTipoUsuario "procurador" %}
	       nuevo_deudor_btn,
	       //{% endifnotequal %} 

	       nuevo_registro_btn, 
	       reporte_btn,
	       'Búsqueda: ',' ',
	       search,
	       '->',
	       imprimir_btn,
	       {
		   text:'Salir',
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
				Ext.MessageBox.alert('Errores', 'Por favor, corrija los errores.');
			    }
			}
			
		    },{
			text: 'Cancelar',
			handler: function(){win.hide();}
		    
		    }]
	    });
	    

    
	// formulario de ingreso de un Evento
	registro_form = new Ext.FormPanel({
		labelAlign: 'right',
		frame:false,
		align:'fit',
		buttonAlign: 'center',
		buttons: [{
			text: 'Guardar',
			handler: function(){
			    var f = registro_form.getForm();
			    if (f.isValid()){			    
				f.submit({
					method:'POST',
					    url:'putevento',
					    success: function(){
					    //Ext.MessageBox.alert('Exitoso', 'Evento guardado');
					    rut_deudor = registro_form.getForm().findField('rut_deudor').value
						registro_form.getForm().reset();
					    registro_form.getForm().findField('rut_deudor').setValue(rut_deudor);
					    
					    registro_win.hide();
					    evento_store.load();
					    //ficha_store.load();
					},
					    failure: function ( result, request) { 
					    Ext.MessageBox.alert('Error', request.result.descripcion); 
					}
				    })
				    }
			    else{
				Ext.MessageBox.alert('Error', 'Por favor, corrija los errores.');
			    }
			}
			
		    },
	{
	    text: 'Cancelar',
	    handler: function(){registro_win.hide();}
	    
	}]
	    });



	registro_form.add (
			   new Ext.form.DateField({
				   fieldLabel: 'Fecha',
				       name: 'fecha',
				       format: 'd/m/Y',
				       value: (new Date()).format('d/m/Y')
				       }),
			   
			   //{% ifnotequal  usuario|getTipoUsuario "procurador" %}
			   new Ext.form.DateField({
				   fieldLabel: 'Fecha Prox Pago',
				       name: 'proximo_pago',
				       format: 'd/m/Y'
				       }),
			   //{% endifnotequal %}
			   
			   new Ext.form.ComboBox({
				   hiddenName: 'receptor',
				       id:'receptor_id',
				       editable:false,
				       allowBlank: true,
				       store: receptor_store,
				       fieldLabel: 'Receptor',
				       displayField: 'nombre',
				       valueField: 'id',
				       emptyText:'Seleccione un receptor',
				       mode: 'local',
				       minChars: 0,
				       name: 'receptor_field',
				       triggerAction:'all'
				       }),

			   {
			       xtype:'numberfield',
				   fieldLabel: 'Gasto Judicial',
				   allowBlank: true,
				   name: 'gasto_judicial'
				   
				   },
			   
			   
			   // campos del administrativo
			   // {% ifnotequal  usuario|getTipoUsuario "procurador" %}	   
			   new Ext.form.ComboBox({
				   hiddenName: 'formapago_codigo',
				       id:'formapago',
				       editable:false,
				       allowBlank: true,
				       store: formapago_store,
				       fieldLabel: 'Forma pago',
				       displayField: 'nombre',
				       valueField: 'codigo',
				       emptyText:'Selec. forma pago',
				       mode: 'local',
				       minChars: 0,
				       name: 'forma_pago',
				       triggerAction:'all'
				       })


			   //{%comment%}
			   ,{
			       xtype:'numberfield',
				   fieldLabel: 'Capital',
				   allowBlank: true,
				   name: 'capital'
				   
				   }
			   ,{
			       xtype:'numberfield',
				   fieldLabel: 'Interes',
				   allowBlank: true,
				   name: 'interes'
				   }
			   ,{
			       xtype:'numberfield',
				    fieldLabel: 'Honorario',
				    allowBlank: true,
				    name: 'honorario'
				   
				   }
			   //{%endcomment%}


			   ,{
				   layout:'column',			       
				   columnWidth: 0.5,
				   items:[ {
				       layout:'form'
					   ,bodyStyle:'padding:0 18px 0 0'
					   ,labelAlign:'left'
					   ,items:[
						   new Ext.form.NumberField({
							   name:'abono'
							       ,fieldLabel:'Abono'
							       ,allowBlank:true
							       ,xtype:'numberfield'
							       })
						   ]
					   }
				       
				       ,new Ext.form.Checkbox({
					       boxLabel:'con tribunales?'
						   ,checked:false
						   })
				       
				       ]
				   },

			   {
			       xtype:'numberfield',
				   fieldLabel: 'Costas',
				   allowBlank: true,
				   name: 'costas'
				   
				   },
			   //{% endifnotequal %}

			   new Ext.form.ComboBox({
				   hiddenName: 'codigo',
				       id:'combo',
				       width: 350,
				       store: codigo_store,
				       allowBlank: false,
				       anyMatch: true,
				       typeAhead: false,
				       fieldLabel: 'Codigo',
				       displayField: 'descripcion',
				       valueField: 'codigo',
				       emptyText:'Seleccione un codigo',
				       mode: 'local',
				       minChars: 0,
				       name: 'codigo',
				       triggerAction:'all',
				       lazyRender:true
				       }),
			   
			   new Ext.form.TextArea({
				   fieldLabel: 'Descripción',
				       name: 'descripcion',
				       grow: true,
				       width: 350,
				       allowBlank: true,
				       preventScrollbars: true
				       }),
			   
			   {
			       xtype: 'hidden',
				   name: 'rut_deudor'
				   }
			   );





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
	new Ext.form.TextField({
		fieldLabel: 'Telefono Fijo',
		name: 'telefono_fijo'
	    }),
	new Ext.form.TextField({
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
				       fieldLabel: 'Fecha asignación',
				       name: 'fecha_creacion',
				       allowBlank:false,
				       format: 'd/m/Y',
				       value: (new Date()).format('d/m/Y')
				   }),
			       new Ext.form.ComboBox({
				       hiddenName: 'sistema_origen',
				       id:'sistorigen',
				       store: sist_orig_store,
				       fieldLabel: 'Sistema Origen',
				       displayField: 'nombre',
				       valueField: 'id',
				       emptyText: 'Sistema origen',
				       mode:'local',
				       minChars: 0,
				       name: 'sistema_origen',
				       allowBlank: true,
				       triggerAction: 'all'
				   })
			       ]

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
				       displayField: 'nombre',
				       valueField: 'rut',
				       emptyText: 'Seleccione un procurador',
				       mode:'local',
				       minChars: 0,
				       name: 'procurador',
				       allowBlank: true,
				       triggerAction: 'all'
				   }),

			       new Ext.form.TextField({
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
				       typeAhead: false,
				       anyMatch: true,
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
				//if (ficha_store.find('rut',rut) == -1){

				f.submit({
					method:'POST',
					    url:'putdeudor',
					    success: function(form, action){
					    Ext.MessageBox.alert('Exitoso', 'Datos guardados');
					    deudor_form.getForm().reset();
					    win.hide();
					    ficha_store.load();
					},
					    failure: function ( result, request) { 
					    Ext.MessageBox.alert('Error', request.result.descripcion); 
					}
				    
				    })

				    //	    }
				    //else {

				    //	Ext.MessageBox.alert("Error", 
				    //		     "El rut ingresado pertenece a un deudor registrado");
				    //}
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
		width: 680,
		height: 400,
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
			     'Capital: {Capital}<br/>'
			     ];
	var bookTpl = new Ext.Template(bookTplMarkup);


	preview = new Ext.FormPanel({
		id: 'preview',
		region: 'east',
		width: 280,
		style: {'margin-left': "0px"},
		cls:'preview',
		autoScroll: true,
		collapsible: true,
		collapsed: true,
		//listeners: FeedViewer.LinkInterceptor,
		split: true,
		items: [

	{
         
            xtype: 'fieldset',
         
            title:'Ficha Deudor',
         
            defaultType: 'textfield',
            autoHeight: true,
            bodyStyle: Ext.isIE ? 'padding:0px -10px 5px 15px;' : 'padding:0px 0px;',
            border: false,
            style: {
                "margin-left": "0px", // when you add custom margin in IE 6...
                "margin-right": Ext.isIE6 ? (Ext.isStrict ? "-10px" : "-13px") : "0"  // you have to adjust for it somewhere else
            },
            items: [
	{
	    xtype: 'datefield',
	    fieldLabel: 'Fecha asign',
	    name: 'fecha'
	},{
	    fieldLabel: 'Nombres',
	    name: 'nombres',
	    width: 130
	},{
	    fieldLabel: 'Apellidos',
	    name: 'apellidos',
	    width: 130
	},{
	    fieldLabel: 'Rut',
	    xtype: 'hidden',
	    name: 'rut',
	    readOnly:true,		
	    width: 130
	},{
	    fieldLabel: 'Rut',
	    name: 'rut_verif',
	    readOnly:true,		
	    width: 130
	},{
	    xtype: 'textarea',
	    fieldLabel: 'Domicilio',
	    name: 'domicilio',
	    width: 130
	},{
	    fieldLabel: 'Tel. Fijo',
	    name: 'telefono_fijo',
	    width: 130
	},{
	    fieldLabel: 'Tel. Oficina',
	    name: 'telefono_oficina',
	    width: 130
	},{
	    fieldLabel: 'Celular',
	    name: 'telefono_movil',
	    width: 130
	},{
	    fieldLabel: 'Rol',
	    name: 'rol',
	    width: 130
	},{
	    fieldLabel: 'Carpeta',
	    name: 'carpeta',
	    width: 130
	},

	new Ext.form.ComboBox({
		hiddenName: 'trib',
		id:'tribunal',
		store: tribunal_store,
		width: 150,
		fieldLabel: 'Tribunal',
		typeAhead: false,
		anyMatch: true,
		displayField: 'nombre',
		valueField: 'nombre',
		emptyText: 'Seleccione un tribunal',
		mode:'local',
		minChars: 0,
		name: 'tribunal',
		allowBlank: true,
		triggerAction: 'all'
	    }),

	new Ext.form.ComboBox({
		hiddenName: 'proc_rut',
		id:'procurador',
		store: procurador_store,
		width: 150,
		fieldLabel: 'Procurador',
		displayField: 'nombre',
		valueField: 'rut',
		emptyText: 'Seleccione un procurador',
		mode:'local',
		minChars: 0,
		name: 'procurador',
		allowBlank: true,
		triggerAction: 'all'
	    }),

	new Ext.form.ComboBox({
		hiddenName: 'sistema_origen',
		id:'sistema_origen_update',
		store: sist_orig_store,
		width: 150,
		fieldLabel: 'Sist. Origen',
		displayField: 'nombre',
		valueField: 'id',
		emptyText: 'Sist. Origen',
		mode:'local',
		minChars: 0,
		name: 'sist_orig_update',
		allowBlank: true,
		triggerAction: 'all'
	    }),

	{
	    fieldLabel: 'Deuda Inicial',
                name: 'deuda_inicial',
		width: 130
		}

		    ]
        }

			],
		buttons: [{
			text: 'Guardar',
			handler: function(){
			    var f = preview.getForm();
			    if (f.isValid()){

				rut = preview.getForm().findField('rut').value.split('-')[0].replace(/\./g,'');
				//if (ficha_store.find('rut',rut) == -1){

				f.submit({
					method:'POST',
					    url:'updatedeudor',
					    success: function(form, action){
					    
					    Ext.MessageBox.alert('Exitoso', 'Datos guardados');
					    deudor_form.getForm().reset();
					    win.hide();
					    ficha_store.load();
					},
					    failure: function ( result, request) { 
					    Ext.MessageBox.alert('Error', request.result.descripcion); 
					}
				    
				    })

				    }
			    else{
				Ext.MessageBox.alert('Error', 'Por favor, corriga los errores.');
			    }
			}
		    },{
			text: 'Cancelar',
			handler: function(){win.hide();}
		    }]
	    });


	var ct = new Ext.Panel({
		renderTo: 'areadata',
		frame: true,
		title: 'Sistema de Deuda',
		//width: 800,
		height: 600,
		layout: 'border',
		tbar: tb,
		split: true,
		items: [
			tabs, preview
			
			]
	    });
	

	//ficha_grid.on('rowclick', function(sm, row, rec) {
	//	record= sm.getStore().getAt(rowIdx);
	//	Ext.getCmp("preview").getForm().loadRecord(rec);
	//   });


	// sm, rowIdx, r
	ficha_grid.on('rowdblclick', function(grid_selected, rowIdx, e) {
		
		record= grid_selected.getStore().getAt(rowIdx);
		grid.enable();
		imprimir_btn.enable();
		nuevo_registro_btn.enable();
		evento_store.baseParams = {rut: record.data.rut};
		evento_store.load();
		grid.show();

		// Agregar rut de deudor en formulario de 
		// nuevo registro
		registro_form.getForm().findField('rut_deudor').setValue(record.data.rut);

		Ext.getCmp("preview").getForm().loadRecord(record);


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
			    Ext.MessageBox.alert('Error', result.responseText); 
			}
		    });


	    });

	
	grid.disable();
	nuevo_registro_btn.disable();
	imprimir_btn.disable();

	ficha_store.load();
	codigo_store.load();
	formapago_store.load();
	procurador_store.load();
	receptor_store.load();
	tribunal_store.load();
	usuario_store.load();
	sist_orig_store.load();
    });