import 'bootstrap-sass';
import $ from 'jquery';
import 'jgrowl/jquery.jgrowl.js';
// Sentry needs Object.assign
import 'core-js/modules/es.object.assign';
import * as Sentry from '@sentry/browser';

import 'mathjax_config';
import UberEditor from 'components/editor';
import { csrfSafeMethod, getCSRFToken, getSections, showComponentError } from './utils';
import sentryOptions from './sentry_conf';

// Configure Sentry SDK
Sentry.init({
  dsn: window.__CSC__.config.sentryDSN,
  ...sentryOptions
});
const userInfo = document.getElementById('login');
if (userInfo) {
  let uid = parseInt(userInfo.getAttribute('data-user-id'));
  if (!isNaN(uid)) {
    Sentry.configureScope(scope => {
      scope.setUser({ id: uid });
    });
  }
}

const CSC = window.__CSC__;

$(document).ready(function () {
  configureCSRFAjax();
  displayNotifications();
  renderText();
  initUberEditors();
  initCollapsiblePanelGroups();

  let sections = getSections();
  if (sections.includes('datetimepickers')) {
    import('components/forms')
      .then(m => {
        m.initDatePickers();
        m.initTimePickers();
      })
      .catch(error => showComponentError(error));
  }
  if (sections.includes('selectpickers')) {
    import('components/forms')
      .then(m => {
        m.initSelectPickers();
      })
      .catch(error => showComponentError(error));
  }
  if (sections.includes('lazy-img')) {
    import(/* webpackChunkName: "lazyload" */ 'components/lazyload')
      .then(m => m.launch())
      .catch(error => showComponentError(error));
  }
  if (sections.includes('components/fileinput')) {
    import(/* webpackChunkName: "fileinput" */ 'components/fileinput')
      .then(m => m.launch())
      .catch(error => showComponentError(error));
  }
  if (sections.includes('gallery')) {
    import(/* webpackChunkName: "gallery" */ 'courses/gallery')
      .then(m => m.launch())
      .catch(error => showComponentError(error));
  }
  // FIXME: combine into one peace `courses`?
  if (sections.includes('courseDetails')) {
    import(/* webpackChunkName: "courseDetails" */ 'courses/courseDetails')
      .then(m => m.launch())
      .catch(error => showComponentError(error));
  }
  if (sections.includes('courseOfferings')) {
    import(/* webpackChunkName: "courseOfferings" */ 'courses/courseOfferings')
      .then(m => m.launch())
      .catch(error => showComponentError(error));
  }
  if (sections.includes('profile')) {
    import(/* webpackChunkName: "profile" */ 'users/profile')
      .then(m => m.launch())
      .catch(error => showComponentError(error));
  }
  if (sections.includes('create-profile')) {
    import(/* webpackChunkName: "profile" */ 'users/createProfile')
      .then(m => m.launch())
      .catch(error => showComponentError(error));
  }
  if (sections.includes('projects/report')) {
    import(/* webpackChunkName: "projects" */ 'projects/report')
      .then(m => m.launch())
      .catch(error => showComponentError(error));
  }
  if (sections.includes('learning/solution')) {
    import(/* webpackChunkName: "solution" */ 'learning/solution')
      .then(m => m.launch())
      .catch(error => showComponentError(error));
  }
});

function displayNotifications() {
  if (window.__CSC__.notifications !== undefined) {
    window.__CSC__.notifications.forEach(message => {
      $.jGrowl(message.text, {
        position: 'bottom-right',
        sticky: message.timeout !== 0,
        theme: message.type
      });
    });
  }
}

function configureCSRFAjax() {
  // Append csrf token on ajax POST requests made with jQuery
  // FIXME: add support for allowed subdomains
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader('X-CSRFToken', getCSRFToken());
      }
    }
  });
}

function renderText() {
  // highlight js and MathJax
  const $ubertexts = $('div.ubertext');
  // Note: MathJax and hljs loads for each iframe separately
  if ($ubertexts.length > 0) {
    UberEditor.preload(function () {
      // Configure highlight js
      hljs.configure({ tabReplace: '    ' });
      // Render Latex and highlight code
      $ubertexts.each(function (i, target) {
        UberEditor.render(target);
      });
    });
  }
}

function initUberEditors() {
  // Replace textarea with EpicEditor
  const $ubereditors = $('textarea.ubereditor');
  UberEditor.cleanLocalStorage($ubereditors);
  $ubereditors.each(function (i, textarea) {
    const editor = UberEditor.init(textarea);
    CSC.config.uberEditors.push(editor);
  });
  if ($ubereditors.length > 0) {
    $('a[data-toggle="tab"]').on('shown.bs.tab', UberEditor.reflowOnTabToggle);
  }
}

function initCollapsiblePanelGroups() {
  $('.panel-group').on('click', '.panel-heading._arrowed', function (e) {
    // Replace js animation with css.
    e.preventDefault();
    const open = $(this).attr('aria-expanded') === 'true';
    $(this).next().toggleClass('collapse').attr('aria-expanded', !open);
    $(this).attr('aria-expanded', !open);
  });
}
