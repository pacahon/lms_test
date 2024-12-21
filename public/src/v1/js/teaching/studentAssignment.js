import { getTemplate, showComponentError } from 'utils';
import { query, toEnhancedHTMLElement } from '@drivy/dom-query';
import { createNotification } from '../utils';
import { FormValidation } from 'components/formValidator';
import { formatWithOptions } from 'date-fns/fp';
import { ru } from 'date-fns/locale';
import { utcToZonedTime } from 'date-fns-tz';

function initAssignmentScoreAuditLog() {
  $('.assignment-score-audit-log').click(function (e) {
    e.preventDefault();
    const modalWrapper = $('#modal-container');
    const template = getTemplate('assignment-score-audit-log-table');
    $.get(this.href, function (data) {
      const header = 'История изменений оценки за задание';
      $('.modal-dialog', modalWrapper).addClass('modal-lg');
      $('.modal-header', modalWrapper).html(
        `${header} <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>`
      );
      const dateToString = formatWithOptions({ locale: ru }, 'd LLL yyyy HH:mm');
      const timeZone = window.__CSC__?.profile?.timezone || 'UTC';
      data.edges.forEach(node => {
        const editor = node.changedBy;
        const fullName = `${editor.lastName} ${editor.firstName} ${editor.patronymic}`.trim();
        node.author = fullName || editor.username;
        node.source = data.sources[node.source];
        const created = new Date(node.createdAt);
        const zonedDate = utcToZonedTime(created, timeZone);
        node.createdAt = dateToString(zonedDate);
      });
      const html = template({ edges: data.edges });
      $('.modal-body', modalWrapper).html(html);
      modalWrapper.modal('show');
    }).fail(data => {
      if (data.status === 403) {
        createNotification('Доступ запрещён.', 'error');
        $(this).remove();
      }
    });
  });
}

function initAssigneeForm() {
  const modalFormWrapper = $('#update-assignee-form');
  modalFormWrapper.modal({
    show: false
  });

  new FormValidation(
    modalFormWrapper.find('form').get(0),
    function (form, data) {
      let assigneeId = data.assignee;
      if (assigneeId === null) {
        assigneeId = '';
      }
      const selectedAssigneeOption = toEnhancedHTMLElement(form).query(
        `select[name="assignee"] option[value="${assigneeId}"]`
      );
      $('#assignee-value').text(selectedAssigneeOption.text);
      createNotification('Изменения успешно сохранены');
      modalFormWrapper.modal('hide');
    },
    function () {
      createNotification('Форма не сохранена. Попробуйте позже.', 'error');
    }
  );
  modalFormWrapper.on('submit', 'form', function (e) {
    e.preventDefault();
    const form = e.target;
    const assigneeSelect = query('#assignee-select');
    const assigneeId = assigneeSelect.value;
    const assigneeName = assigneeSelect.options[assigneeSelect.selectedIndex].text;
    $.ajax({
      method: 'PUT',
      url: form.getAttribute('action'),
      dataType: 'json',
      data: {
        assignee: assigneeId
      }
    })
      .done(data => {
        $('#assignee-value').text(assigneeName);
      })
      .fail(xhr => {
        createNotification('Something went wrong', 'error');
        console.log(xhr);
      });
  });
}

const fn = {
  launch: function () {
    initAssigneeForm();
    import('components/forms')
      .then(m => {
        m.initSelectPickers();
      })
      .catch(error => showComponentError(error));
    initAssignmentScoreAuditLog();
  }
};

export default fn;
