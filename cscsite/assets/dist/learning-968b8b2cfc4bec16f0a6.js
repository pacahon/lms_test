webpackJsonp([14],{Tap1:function(t,e,i){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var n=i("0iPh"),o=i.n(n),a=i("mwlq"),r=i("mF0L"),c=o()("#o-sidebar"),f=o()(".footer"),s=o()(".assignment-comment"),u=o()("#submission-comment-model-form"),d=void 0,m={Launch:function(){m.initCommentModal(),m.initStickySidebar()},initCommentModal:function(){u.modal({show:!1}),u.on("shown.bs.modal",function(t){var e=o()(t.target).find("textarea").get(0);d=a.default.init(e),u.css("opacity","1")}),o()(".__edit",s).click(function(t){t.preventDefault();var e=o()(this);o.a.get(this.href,function(t){u.css("opacity","0"),o()(".inner",u).html(t),u.modal("toggle")}).fail(function(t){if(403===t.status){Object(r.a)("Доступ запрещён. Вероятно, время редактирования комментария истекло.","error"),e.remove()}})}),u.on("submit","form",m.submitEventHandler)},submitEventHandler:function(t){t.preventDefault();var e=t.target;return o.a.ajax({url:e.action,type:"POST",data:o()(e).serialize()}).done(function(t){if(1===t.success){u.modal("hide");var e=s.filter(function(){return o()(this).data("id")==t.id}),i=o()(".ubertext",e);i.html(t.html),a.default.render(i.get(0)),Object(r.a)("Комментарий успешно сохранён.")}else Object(r.a)("Комментарий не был сохранён.","error")}).fail(function(){Object(r.a)("Комментарий не был сохранён.","error")}),!1},initStickySidebar:function(){var t=c.offset().top-20;f.offset().top-75-t>500&&(c.affix({offset:{top:t,bottom:f.outerHeight(!0)}}),c.affix("checkPosition"))}};o()(document).ready(function(){m.Launch()})}},["Tap1"]);