function create_search_result(e,t){var a=$("<li></li>"),n=$("<a></a>"),o=$("<h4></h4>"),c=$("<span></span>");return n.attr("href",t.url),n.text(t.name),o.append(n),c.text(t.description),a.append(o),a.append(c),a}function autocomplete_search(){$("ul.autocomplete-search").each((function(){var e=$(this);e.hide();var t=e.attr("for"),a=e.attr("action"),n="/autocomplete-"+a+"/",o=e.attr("method"),c=$('input[name="'+t+'"]'),r=null;c.keyup((function(){r&&clearTimeout(r),r=setTimeout((function(){var t=c.val();if(""==t)return e.empty(),void e.hide(300);var r=$("<span></span>");r.addClass("loader"),$.ajax({url:n,method:o,data:{search:t},success:function(t){e.empty();for(var n=0;n<t.matching_results.length;n++){var o=create_search_result(a,t.matching_results[n]);e.append(o)}t.matching_results.length>0?e.show(300):e.hide(300)},complete:function(){r.remove()}})}),50)}))}))}$(document).ready((function(){$("input.autocomplete-field").each((function(){var e=$(this);e.autocomplete({source:function(t,a){var n="/autocomplete-"+e.attr("action")+"/";$.getJSON(n,{search:t.term,only_name:!0},(function(e){a(e.matching_results)}))},minLength:2,select:function(e,t){console.log(t.item.value)}})}))})),$(document).ready(autocomplete_search);