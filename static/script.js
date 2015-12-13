var main = function() {
    $('#submit').addClass('disabled');
    $('#inputText').keyup(function() {
                          var postLength = $('#inputText').val().length;
                          var charactersLeft = 999 - postLength;
                          $('.pcounter').text(charactersLeft);
                          if(charactersLeft >= 998 ) {
                          $('#submit').addClass('disabled');
                          }
                          else {
                          $('#submit').removeClass('disabled');
                          }
                          });
}

$(document).ready(main);

$(document).ready(function() {
                  
                  $('.deleteButton').on('click', function() {
                                        check = confirm("hi")
                                        if (check == true) {
                                        alert("true")
                                        }
                                        else {
                                        alert("false")
                                        
                                        }
                                        
                                        });
                  });

