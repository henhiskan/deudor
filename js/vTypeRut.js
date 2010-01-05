/**
 * SCI JS Copyright(c) Init5 Ltd 2009, 
 * 
 * GNU GPL license v3.
 *
 * Authors: Carlos Roman and Juan Rivas
 * 
 */

Ext.apply(Ext.form.VTypes, {

   Rut: function(val, field){
	var tmpstr = "";
	var intlargo = val;
	if (intlargo.length> 0)
	{
        crut = val;
		largo = crut.length;
		if ( largo <2 )
		{
			return false;
		}
		for ( i=0; i <crut.length ; i++ )
                    if ( crut.charAt(i) != ' ' && crut.charAt(i) != '.' && crut.charAt(i) != '-' )
                        {
			tmpstr = tmpstr + crut.charAt(i);
                        }
		rut = tmpstr;
		crut=tmpstr;
		largo = crut.length;
	
		for (i=0; i < largo ; i++ )	 
		{			 
			if ( tmpstr.charAt(i) !="0" && tmpstr.charAt(i) != "1" && tmpstr.charAt(i) !="2" && tmpstr.charAt(i) != "3" && tmpstr.charAt(i) != "4" && tmpstr.charAt(i) !="5" && tmpstr.charAt(i) != "6" && tmpstr.charAt(i) != "7" && tmpstr.charAt(i) !="8" && tmpstr.charAt(i) != "9" && tmpstr.charAt(i) !="k" && tmpstr.charAt(i) != "K" ) 
 			{			 
				return false;		 
			}	 
		}

		var invertido = "";	 
		for ( i=(largo-1),j=0; i>=0; i--,j++ )		 
                    invertido = invertido + tmpstr.charAt(i);	 
		var dtexto = "";	 
		dtexto = dtexto + invertido.charAt(0);	 
		dtexto = dtexto + '-';	 
		cnt = 0;	 
 
		for ( i=1,j=2; i<largo; i++,j++ )	 
		{		 
			if ( cnt == 3 )		 
			{			 
				dtexto = dtexto + '.';			 
				j++;			 
				dtexto = dtexto + invertido.charAt(i);			 
				cnt = 1;		 
			}			 
			else		 
			{				 
				dtexto = dtexto + invertido.charAt(i);			 
				cnt++;		 
			}	 
		}	 
 
		invertido = "";	 
		for ( i=(dtexto.length-1),j=0; i>=0; i--,j++ )		 
			invertido = invertido + dtexto.charAt(i);

		if ( largo> 2 )
			rut = crut.substring(0, largo - 1);
		else
			rut = crut.charAt(0);
	
		dv = crut.charAt(largo-1);
		dv = dv + "";	 
		if ( dv != '0' && dv != '1' && dv != '2' && dv != '3' && dv != '4' && dv != '5' && dv != '6' && dv != '7' && dv != '8' && dv != '9' && dv != 'k'  && dv != 'K')	 
                    {		 
			return false;	 
                    }	
		if ( rut == null || dv == null )
                    return 0;
	
		var dvr = '0';
		suma = 0;
		mul  = 2;
	
		for (i= rut.length-1 ; i>= 0; i--)
                    {
			suma = suma + rut.charAt(i) * mul;
			if (mul == 7)
				mul = 2;
			else
				mul++;
                    }
	
		res = suma % 11;
		if (res==1)
			dvr = 'k';
		else if (res==0)
			dvr = '0';
		else
		{
			dvi = 11-res;
			dvr = dvi + "";
		}
	
		if ( dvr != dv.toLowerCase() )
		{
			return false;
		}
		return true;
	}
}
});
