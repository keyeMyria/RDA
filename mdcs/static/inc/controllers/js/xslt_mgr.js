/**
 * Show a dialog when a template is selected
 */
displayImport = function()
{
 $(function() {
    $("#form_start_errors").html("");
    $( "#dialog-message" ).dialog({
      modal: true,
      width: 500,
      buttons:
    	  [
           {
               text: "Upload",
               click: function() {
                    if(validateExport())
                    {
                       var formData = new FormData($( "#form_start" )[0]);
	            	   $.ajax({
	            	        url: "/admin/xml-schemas/manage-xslt",
	            	        type: 'POST',
	            	        data: formData,
	            	        cache: false,
	            	        contentType: false,
	            	        processData: false,
	            	        async:false,
	            	   		success: function(data){
	            	   		    $( "#dialog-success" ).dialog({
                                modal: true,
                                buttons: {
                                Ok: function() {
                                    $( this ).dialog( "close" );
                                    window.location = '/admin/xml-schemas/manage-xslt'
                                  },
                                }
                                });
	            	        },
	            	        error:function(data){
	            	        	$("#form_start_errors").html(data.responseText);
	            	        },
	            	    })
	            	    ;
                    }
               }
           }
          ]
    });
  });
}

validateExport = function()
{
    errors = ""
    if ($( "#id_name" ).val().trim() == ""){
        errors = "Please enter a name."
    }
	// check if an option has been selected
    else if ($( "#id_xslt_file" ).val() == ""){
        errors = "Please select an XSLT file."
    }

	if (errors != ""){
		$("#form_start_errors").html(errors);
		return (false);
	}else{
		return (true)
	}
}

deleteXSLT = function(xslt_id)
{
 $(function() {
    $( "#dialog-deletexslt-message" ).dialog({
      modal: true,
      buttons:{
            	Delete: function() {
            		delete_XSLT(xslt_id);
            		$( this ).dialog( "close" );
            		},
				Cancel: function() {
	                $( this ).dialog( "close" );
		          },
		    }
    });
  });
}

/**
 * AJAX call, deletes an XSLT File
 * @param bucket_id id of the bucket
 */
delete_XSLT = function(xslt_id){
    $.ajax({
        url : "/admin/xml-schemas/delete-xslt",
        type : "POST",
        dataType: "json",
        data : {
        	xslt_id : xslt_id,
        },
        success: function(data){
            $( "#dialog-success-delete" ).dialog({
                modal: true,
                buttons: {
                Ok: function() {
                    $( this ).dialog( "close" );
                    window.location = '/admin/xml-schemas/manage-xslt'
                  },
                }
            });
        },
        error:function(data){
            $("#form_start_errors").html(data.responseText);
            $( "#form_start_errors").dialog({
                modal: true,
                buttons: {
                Ok: function() {
                    $( this ).dialog( "close" );
                  },
                }
            });
	    }
    });
}


Init = function(){
    $('.edit').on('click',editInformation);
    var buttonsetElts = $("td[id^=ButtonSet]")
    $.each(buttonsetElts, function(index, props) {
         $("#"+props.id).buttonset();
    });

}

/**
 * Edit general information of a template or a type
 */
editInformation = function(objectID)
{
    var objectName = $(this).parent().siblings(':first').text();
    var objectID = $(this).attr("objectid");
    $("#form_edit_errors").html("");

    $("#edit-name")[0].value = objectName;

	$(function() {
        $( "#dialog-edit-message" ).dialog({
            modal: true,
            width: 500,
            buttons: {
            	Ok: function() {
					var newName = $("#edit-name")[0].value;
					edit_information(objectID, newName);
                },
                Cancel: function() {
                    $( this ).dialog( "close" );
                }
            }
        });
    });
}


/**
 * AJAX call, edit information of an object
 * @param objectID id of the object
 * @param newName new name of the object
 */
edit_information = function(objectID, newName, newFilename, newAvailableForAll){
    $.ajax({
        url : "/admin/xml-schemas/edit-xslt",
        type : "POST",
        dataType: "json",
        data : {
        	object_id : objectID,
        	new_name : newName,
        },
        success: function(data){
           $( "#dialog-success-update" ).dialog({
                modal: true,
                buttons: {
                Ok: function() {
                    $( this ).dialog( "close" );
                    window.location = '/admin/xml-schemas/manage-xslt'
                  },
                }
            });
        },
        error:function(data){
            $("#form_edit_errors").html(data.responseText);
        }
    });
}


/**
 * Display error message when bad edition of type
 */
showErrorEditType = function(){
	$(function() {
        $( "#dialog-error-edit" ).dialog({
            modal: true,
            buttons: {
			Ok: function() {
                $( this ).dialog( "close" );
	          },
		    }
        });
    });
}
