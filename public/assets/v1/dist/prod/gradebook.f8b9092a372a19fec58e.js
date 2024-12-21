"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[221],{58788:function(e,t,n){n.r(t);n(58188),n(49228),n(26936),n(68995),n(43450),n(16781);var r=n(41604),o=n.n(r),a=n(86563),i=n(88744),s=$(".marks-sheet-csv-link"),c=$("#marks-sheet-save"),u=$("#gradebook-container"),l=$("#gradebook"),f=$(".gradebook__controls");function d(e){return e.value!==e.getAttribute("initial")}var m={launch:function(){m.restoreStates(),m.finalGradeSelects(),m.submitForm(),m.downloadCSVButton(),m.onChangeAssignmentGrade(),m.scrollButtons(),m.importYandexContestProblemForm()},restoreStates:function(){var e=document.querySelectorAll("#gradebook .__input");Array.prototype.forEach.call(e,m.toggleState);var t=document.querySelectorAll("#gradebook select");Array.prototype.forEach.call(t,m.toggleState)},downloadCSVButton:function(){s.click((function(){if(l.find(".__unsaved").length>0)return o()({title:"",text:"Сперва сохраните форму,\nчтобы скачать актуальные данные.",type:"warning",confirmButtonText:"Хорошо"}),!1}))},submitForm:function(){c.click((function(){$("form[name=gradebook]").submit()})),$("form[name=gradebook]").submit((function(e){var t=this.querySelectorAll(".__input, .__final_grade select");Array.prototype.forEach.call(t,(function(e){if(!d(e)){e.disabled=!0;var t="input[name=initial-".concat(e.name,"]");document.querySelector(t).disabled=!0}}))}))},finalGradeSelects:function(){l.on("change","select",(function(e){m.toggleState(e.target)}))},onChangeAssignmentGrade:function(){l.on("change","input.__assignment",(function(e){m.toggleState(e.target)}))},toggleState:function(e){var t;"input"===e.nodeName.toLowerCase()?t=e:"select"===e.nodeName.toLowerCase()&&(t=e.parentElement),d(e)?t.classList.add("__unsaved"):t.classList.remove("__unsaved")},scrollButtons:function(){u.width()<=l.outerWidth()&&(f.on("click",".scroll.left",(function(){m.scroll(-1)})),f.on("click",".scroll.right",(function(){m.scroll(1)})),f.css("visibility","visible"))},scroll:function(e){var t=100*parseInt(e);if(0!==t){var n=u.scrollLeft();u.scrollLeft(n+t)}},importYandexContestProblemForm:function(){var e=(0,i.Z)((function(e,t){$.ajax({method:"POST",url:e,dataType:"json",data:{assignment:t}}).done((function(e){(0,a.sc)("Баллы успешно импортированы, страница будет перезагружена","info"),setTimeout((function(){return window.location.reload()}),500)})).fail((function(e){var t;e.responseJSON&&void 0!==e.responseJSON.errors?t=e.responseJSON.errors.map((function(e){return e.message})).join("<br/>"):t="".concat(e.statusText,". Try again later.");e.status>=500&&e.status<600?(0,a.sc)(t,"error",{sticky:!0}):(0,a.sc)(t,"error")}))}),1e3,{leading:!0,trailing:!1});var t=$("#import-scores-from-yandex-contest");t.on("submit","form",(function(n){n.preventDefault();var r=n.target,o=r.querySelector("select[name=assignment]").value||null;null!==o&&(e(r.getAttribute("action"),o),t.modal("hide"))}))}};t.default=m},30490:function(e,t,n){n.r(t),n.d(t,{default:function(){return p}});n(58188),n(1939),n(45794),n(18178),n(49228),n(15735),n(73439),n(28673),n(6886);var r=n(86563),o={isEnhancedHTMLElement:!0,on:function(e,t,n){var r=this,o=function o(a){t.call(a.target,a),n&&n.once&&r.removeEventListener(e,o)};return this.addEventListener(e,o),function(){r.removeEventListener(e,o)}},onDelegate:function(e,t,n,r){var o=this,a=function a(i){i&&i.target&&i.target.matches(e)&&(n.call(i.target,i),r&&r.once&&o.removeEventListener(t,a))};return this.addEventListener(t,a),function(){o.removeEventListener(t,a)}},query:s,queryStrict:function(e){var t=this instanceof HTMLElement?this.query(e):s(e);if(!t)throw new Error("Unexisting HTML element: "+e);return t},queryAll:function(e){var t=this instanceof HTMLElement?this:document,n=Array.from(t.querySelectorAll(e));return c(n)}},a={isEnhancedHTMLElementList:!0,on:function(e,t,n){var r=[];return this.forEach((function(o){var a=o.on(e,t,n);r.push(a)})),function(){r.forEach((function(e){return e()}))}},onDelegate:function(e,t,n,r){var o=[];return this.forEach((function(a){var i=a.onDelegate(e,t,n,r);o.push(i)})),function(){o.forEach((function(e){return e()}))}}},i=function(e){return Object.assign(e,o)};function s(e){var t=(this instanceof HTMLElement?this:document).querySelector(e);return t?i(t):null}var c=function(e){var t=e.map((function(e){return i(e)}));return Object.assign(t,a)};var u=n(38777),l=n(9249),f=n(87371),d=(n(27233),n(26936),n(16781),n(43450),function(){function e(t,n,r){(0,l.Z)(this,e),this.form=t,this.submitButton=t.querySelector('[type="submit"]'),this.isValidCallback=n,this.isInvalidCallback=r,this.onSubmitFormHandler=this.onSubmitFormHandler.bind(this),this.submitButton.addEventListener("click",this.onSubmitFormHandler)}return(0,f.Z)(e,[{key:"onSubmitFormHandler",value:function(e){e.preventDefault();var t=[];Array.from(this.form.elements).forEach((function(e){if(e.name){var n="".concat(encodeURIComponent(e.name),"=").concat(encodeURIComponent(e.value));t.push(n)}})),this.validateForm(t.join("&"))}},{key:"validateForm",value:function(e){var t=this;$.ajax({method:"PUT",url:this.form.getAttribute("action"),contentType:"application/x-www-form-urlencoded",dataType:"json",data:e}).done((function(e){t.clearErrorMessages(),t.isValidCallback(t.form,e)})).fail((function(e){var n=JSON.parse(e.responseText);t.clearErrorMessages(),t.applyErrorMessages(n),t.isInvalidCallback(t.form,n)}))}},{key:"clearErrorMessages",value:function(){var e=this.form.querySelectorAll(".error-message");e.length&&(0,u.Z)(e).map((function(e){var t=e.closest(".form-group");null!==t&&t.classList.remove("has-error"),e.remove()}))}},{key:"applyErrorMessages",value:function(e){for(var t in e)"non_field_errors"===t?this._handleNonFieldErrors(e[t]):this._handleFieldErrors(e[t],t)}},{key:"_handleNonFieldErrors",value:function(e){for(var t=this.form.querySelector(".non_field_errors"),n=0;n<e.length;n++){var r=e[n];t.appendChild(this._newError(" - ".concat(r)))}}},{key:"_handleFieldErrors",value:function(e,t){var n=this.form.querySelector('[name="'.concat(t,'"]'));if(n)for(var r=0;r<e.length;r++)n.closest(".form-group").append(this._newError(e[r])),n.closest(".form-group").classList.add("has-error")}},{key:"_newError",value:function(e){var t=document.createElement("div");return t.className="error-message",t.appendChild(document.createTextNode(e)),t}}]),e}()),m=n(37985),v=n(87912),h=n(22601);var g={launch:function(){var e;(e=$("#update-assignee-form")).modal({show:!1}),new d(e.find("form").get(0),(function(t,n){var o=n.assignee;null===o&&(o="");var a=i(t).query('select[name="assignee"] option[value="'.concat(o,'"]'));$("#assignee-value").text(a.text),(0,r.sc)("Изменения успешно сохранены"),e.modal("hide")}),(function(){(0,r.sc)("Форма не сохранена. Попробуйте позже.","error")})),e.on("submit","form",(function(e){e.preventDefault();var t=e.target,n=s("#assignee-select"),o=n.value,a=n.options[n.selectedIndex].text;$.ajax({method:"PUT",url:t.getAttribute("action"),dataType:"json",data:{assignee:o}}).done((function(e){$("#assignee-value").text(a)})).fail((function(e){(0,r.sc)("Something went wrong","error"),console.log(e)}))})),Promise.all([n.e(304),n.e(426)]).then(n.bind(n,59426)).then((function(e){e.initSelectPickers()})).catch((function(e){return(0,r.Wd)(e)})),$(".assignment-score-audit-log").click((function(e){var t=this;e.preventDefault();var n=$("#modal-container"),o=(0,r.t4)("assignment-score-audit-log-table");$.get(this.href,(function(e){var t,r;$(".modal-dialog",n).addClass("modal-lg"),$(".modal-header",n).html("".concat("История изменений оценки за задание",' <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>'));var a=(0,m.Z)({locale:v.Z},"d LLL yyyy HH:mm"),i=(null===(t=window.__CSC__)||void 0===t||null===(r=t.profile)||void 0===r?void 0:r.timezone)||"UTC";e.edges.forEach((function(t){var n=t.changedBy,r="".concat(n.lastName," ").concat(n.firstName," ").concat(n.patronymic).trim();t.author=r||n.username,t.source=e.sources[t.source];var o=new Date(t.createdAt),s=(0,h.utcToZonedTime)(o,i);t.createdAt=a(s)}));var s=o({edges:e.edges});$(".modal-body",n).html(s),n.modal("show")})).fail((function(e){403===e.status&&((0,r.sc)("Доступ запрещён.","error"),$(t).remove())}))}))}},p=g},53914:function(e,t,n){n.d(t,{Z:function(){return y}});var r=n(93122),o=n(93221),a=function(){return o.Z.Date.now()},i=/\s/;var s=function(e){for(var t=e.length;t--&&i.test(e.charAt(t)););return t},c=/^\s+/;var u=function(e){return e?e.slice(0,s(e)+1).replace(c,""):e},l=n(22758),f=/^[-+]0x[0-9a-f]+$/i,d=/^0b[01]+$/i,m=/^0o[0-7]+$/i,v=parseInt;var h=function(e){if("number"==typeof e)return e;if((0,l.Z)(e))return NaN;if((0,r.Z)(e)){var t="function"==typeof e.valueOf?e.valueOf():e;e=(0,r.Z)(t)?t+"":t}if("string"!=typeof e)return 0===e?e:+e;e=u(e);var n=d.test(e);return n||m.test(e)?v(e.slice(2),n?2:8):f.test(e)?NaN:+e},g=Math.max,p=Math.min;var y=function(e,t,n){var o,i,s,c,u,l,f=0,d=!1,m=!1,v=!0;if("function"!=typeof e)throw new TypeError("Expected a function");function y(t){var n=o,r=i;return o=i=void 0,f=t,c=e.apply(r,n)}function b(e){return f=e,u=setTimeout(S,t),d?y(e):c}function E(e){var n=e-l;return void 0===l||n>=t||n<0||m&&e-f>=s}function S(){var e=a();if(E(e))return k(e);u=setTimeout(S,function(e){var n=t-(e-l);return m?p(n,s-(e-f)):n}(e))}function k(e){return u=void 0,v&&o?y(e):(o=i=void 0,c)}function _(){var e=a(),n=E(e);if(o=arguments,i=this,l=e,n){if(void 0===u)return b(l);if(m)return clearTimeout(u),u=setTimeout(S,t),y(l)}return void 0===u&&(u=setTimeout(S,t)),c}return t=h(t)||0,(0,r.Z)(n)&&(d=!!n.leading,s=(m="maxWait"in n)?g(h(n.maxWait)||0,t):s,v="trailing"in n?!!n.trailing:v),_.cancel=function(){void 0!==u&&clearTimeout(u),f=0,o=l=i=u=void 0},_.flush=function(){return void 0===u?c:k(a())},_}},88744:function(e,t,n){var r=n(53914),o=n(93122);t.Z=function(e,t,n){var a=!0,i=!0;if("function"!=typeof e)throw new TypeError("Expected a function");return(0,o.Z)(n)&&(a="leading"in n?!!n.leading:a,i="trailing"in n?!!n.trailing:i),(0,r.Z)(e,t,{leading:a,maxWait:t,trailing:i})}}}]);