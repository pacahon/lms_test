import $ from 'jquery';
import 'jasny-bootstrap/js/fileinput';

export function launch() {
  $('.jasny.fileinput')
    .on('clear.bs.fileinput', function (event) {
      $(event.target).find('.fileinput-clear-checkbox').val('on');
      $(event.target).find('.fileinput-filename').text('Файл не выбран');
    })
    .on('change.bs.fileinput', function (event) {
      $(event.target).find('.fileinput-clear-checkbox').val('');
    })
    .on('reseted.bs.fileinput', function (event) {
      $(event.target).find('.fileinput-filename').text('Файл не выбран');
      $(event.target).find('.fileinput-clear-checkbox').val('');
    });
}
