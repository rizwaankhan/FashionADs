function fnFormatDetails ( oTable, nTr )
{
    var x = "value=\"";
    var y = "\">";
    var aData = oTable.fnGetData( nTr );
    var id = aData[1].slice(aData[1].indexOf(x)+x.length,aData[1].length-2);
    var sOut = '<table class="align-self-center text-center" cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">';
    sOut += '<thead<tr><th>#</th><th>Variation Title</th><th>Variation Discription</th><th>Price</th> <th>Discount</th></tr></thead><tbody id="'+id+'"></tbody></table>';
    $.ajax({
        type : 'POST',
        url : 'getvariations/',
        dataType : 'json',
        async : true,
        data:{
            "id":id,
            'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val()
        },
        success: function(json){
            var out;
            json.Data.forEach(function (element) {
                out += '<tr><td style="width: 10px">' +
                    '<input type="radio" required  name="select"  id="select" value="a'+element[0]+'" ></td>' +
                    '<td>'+element[1]+'</td>' +
                    ' <td>'+element[2]+'</td>' +
                    ' <td>'+element[3]+'</td>' +
                    '<td>'+element[4]+'% OFF</td></tr>';

             });
            $("#"+id).append(out);

        }
    });


    return sOut;

}

$(document).ready(function() {

    $('#dynamic-table').dataTable( {
        // "aaSorting": [[ 4, "desc" ]]
    } );

    /*
     * Insert a 'details' column to the table
     */
    var nCloneTh = document.createElement( 'th' );
    var nCloneTd = document.createElement( 'td' );
    nCloneTd.innerHTML = '<img src="/static/img/details_open.png">';
    nCloneTd.className = "center";

    $('#hidden-table-info thead tr').each( function () {
        this.insertBefore( nCloneTh, this.childNodes[0] );
    } );

    $('#hidden-table-info tbody tr').each( function () {
        this.insertBefore(  nCloneTd.cloneNode( true ), this.childNodes[0] );
    } );

    /*
     * Initialse DataTables, with no sorting on the 'details' column
     */
    var oTable = $('#hidden-table-info').dataTable( {
        "aoColumnDefs": [
            { "bSortable": false, "aTargets": [ 0 ] }
        ],
        "aaSorting": [[1, 'asc']]
    });

    /* Add event listener for opening and closing details
     * Note that the indicator for showing which row is open is not controlled by DataTables,
     * rather it is done here
     */
    $(document).on('click','#hidden-table-info tbody td img',function () {
        var nTr = $(this).parents('tr')[0];
        if ( oTable.fnIsOpen(nTr) )
        {
            /* This row is already open - close it */
            this.src = "/static/img/details_open.png";
            oTable.fnClose( nTr );
        }
        else
        {
            /* Open this row */
            this.src = "/static/img/details_close.png";
            oTable.fnOpen( nTr, fnFormatDetails(oTable, nTr), 'details' );
        }
    } );
} );




$(document).ready(function() {

    $('.dynamic-table').dataTable( {
        // "aaSorting": [[ 4, "desc" ]]
    } );

    /*
     * Insert a 'details' column to the table
     */
    var nCloneTh = document.createElement( 'th' );
    var nCloneTd = document.createElement( 'td' );
    nCloneTd.innerHTML = '<img src="/static/img/details_open.png">';
    nCloneTd.className = "center";

    $('#hidden-table-info thead tr').each( function () {
        this.insertBefore( nCloneTh, this.childNodes[0] );
    } );

    $('#hidden-table-info tbody tr').each( function () {
        this.insertBefore(  nCloneTd.cloneNode( true ), this.childNodes[0] );
    } );

    /*
     * Initialse DataTables, with no sorting on the 'details' column
     */
    var oTable = $('#hidden-table-info').dataTable( {
        "aoColumnDefs": [
            { "bSortable": false, "aTargets": [ 0 ] }
        ],
        "aaSorting": [[1, 'asc']]
    });

    /* Add event listener for opening and closing details
     * Note that the indicator for showing which row is open is not controlled by DataTables,
     * rather it is done here
     */
    $(document).on('click','#hidden-table-info tbody td img',function () {
        var nTr = $(this).parents('tr')[0];
        if ( oTable.fnIsOpen(nTr) )
        {
            /* This row is already open - close it */
            this.src = "/static/img/details_open.png";
            oTable.fnClose( nTr );
        }
        else
        {
            /* Open this row */
            this.src = "/static/img/details_close.png";
            oTable.fnOpen( nTr, fnFormatDetails(oTable, nTr), 'details' );
        }
    } );
} );

