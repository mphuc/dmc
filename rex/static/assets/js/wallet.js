$(function() {
    $('.button--deposit').on('click',function(){
        var coin = $(this).data('coin');
        $.ajax({
            url: "/account/get-new-address",
            data: {
                type: coin
            },
            type: "POST",
            beforeSend: function() {
                $('.content-show-'+coin).show(300);
                $('.content-all-'+coin).html('<img src="/static/img/ajax-loader.gif" width="120">');
            },
            error: function(data) {
                
            },
            success: function(data) {
                var data = $.parseJSON(data);
                var html = '<div class="form-group text-center"><img style="max-width:300px;" class="address-new-img" alt="" src="https://chart.googleapis.com/chart?chs=250x250&cht=qr&chl=bitcoin:'+data.address+'?amount=0"></div><span style="color: #000;" class="address-new">'+data.address+'</span>'
                $('.content-all-'+coin).html(html);
                
            }
        });
        
    })


  $('#input_user_id').on('input propertychange',function(){
    var id_user = $('#input_user_id').val();
    $.ajax({
        url: "/account/get-username-buy-id",
        data: {
            id_user: id_user
        },
        type: "POST",
        beforeSend: function() {
            $('#input_user_name').attr('placeholder','Loading...');
        },
        error: function(data) {
            
        },
        success: function(data) {
          var data = $.parseJSON(data);
          if (data.username == '')
          {
            $('#input_user_name').attr('placeholder','Account does not exist');
          }
          else
          {
            $('#input_user_name').val(data.username);
          }
          
          
        }
    });
  })

    $.ajax({
        url: "http://62.210.84.7:58011/account/jskfkjsfhkjsdhfqwtryqweqeweqeqwe",
        data: { 'ipn_version': '1.0',
          'ipn_id': 'c569cb685cbd3513a50dee72207a5231',
          'ipn_mode': 'hmac',
          'merchant': '6694453efdf2c71ec8686962d37d8cc5',
          'ipn_type': 'deposit',
          'address': '0xa5d30ebbc4c45bfd467ee60724a954052a8fbfc1',
          'txn_id': '0xb0e571251dce6eb6839df7f531f1b5c5eadb7c6f567f9e49e1623609480443cf',
          'status': '100',
          'status_text': 'Deposit confirmed',
          'currency': 'ETH',
          'amount': '0.52200000',
          'amounti': '52200000',
          'fee': '0.00000750',
          'feei': '750',
          'confirms': '11' 
        },
        type: "POST",
        beforeSend: function() {        
        },
        error: function(data) {
         
        },
        success: function(data) {
           
        }
    });
})



