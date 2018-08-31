$(function(){
    getInfo();
    getPrice();
    // Socket();
   
    function getInfo() {
        setTimeout(function() {
            //  $('.main-panel').css({'background-image' : 'url(/static/assets/img/smartfva-bg.jpg)'});
            //  $('#personal.main-panel').css({'background-color' : '#fff', 'background-image' : 'none'});
            // $('.sidebar-wrapper').css({'background-image' : 'url(/static/assets/img/smartfva-bg.jpg)'});
            $('.sidebar-wrapper').removeClass('re-loading');
            $('.main-panel').removeClass('re-loading');
        }, 100);
        /*$.get("/getBalance", function(data) {
            var data = $.parseJSON(data);
            
            $('.usd_balance').html(parseFloat(data.usd_balance).toFixed(2));
            $('.total_earn').html(parseFloat(data.total_earn).toFixed(2));
            $('.total_invest').html(parseFloat(data.total_invest).toFixed(2));
            $('.total_capital_back').html(parseFloat(data.total_capital_back).toFixed(2));
          
           
        });*/
    }
    function Socket(){
        namespace = '/SmartFVA';
        var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
        socket.on('connect', function() {
            socket.emit('getInfo', {data: 'I\'m connected!'});
            socket.emit('getBalance', {data: 'I\'m connected!'});
            
            
        });
        socket.on('my_response', function(data) {
            $('.btc_usd').val(data.btc_usd);
            $('.sva_btc').val(data.sva_btc);
            $('.sva_usd').val(data.sva_usd);
            $('.sva_usd').html(data.sva_usd);
            $('.rate_sva_usd').html(data.sva_usd+ ' USD');
            $('.rate_btc_usd').html(data.btc_usd + ' USD');
            var sva_btc = (parseFloat(data.sva_usd)/parseFloat(data.btc_usd)).toFixed(8)
            $('.rate_sva_btc').html(parseFloat(sva_btc+ ' BTC'));
        });
        
    }
    setInterval(function(){ getPrice(); }, 30000);
    function getPrice(){
        $.getJSON("/getInfo", function(data) {
             $('.btc_usd').val(data.btc_usd);
                $('.sva_btc').val(data.sva_btc);
                $('.sva_usd').val(data.sva_usd);
                $('.sva_usd').html(data.sva_usd);
                $('.rate_sva_usd').html(data.sva_usd+ ' USD');
                $('.rate_btc_usd').html(data.btc_usd + ' USD');
                var sva_btc = (parseFloat(data.sva_usd)/parseFloat(data.btc_usd)).toFixed(8)
                $('.rate_sva_btc').html(parseFloat(sva_btc+ ' BTC'));
           
        });
    }

});
