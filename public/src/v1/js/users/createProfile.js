import { createNotification, showComponentError } from '../utils';
import FileAPI from 'fileapi/dist/FileAPI';
import _throttle from 'lodash-es/throttle';

const photoRequirements = {
  minWidth: 250,
  minHeight: 350,
  maxFileSize: 3, // Mb
  minThumbWidth: 170,
  minThumbHeight: 238,
  mimeTypes: ['image/jpeg', 'image/png']
};

function handleSubmitCode() {
  const email = $('input[name="confirmation-email"]').val();
  if (email.length > 0) {
    console.debug('send validation email');
    const emailVerificationData = Object.assign({}, window.emailVerificationData);

    $.ajax({
      type: 'POST',
      url: '/api/admission/confirmation/verify-email',
      data: {
        ...emailVerificationData,
        email
      },
      dataType: 'json'
    })
      .done(function (data) {
        createNotification('Код был отправлен на указанный email.', 'info');
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        createNotification('Email не был отправлен.', 'error');
      });
  }
}

const throttledSubmitCode = _throttle(handleSubmitCode, 1000, { leading: true, trailing: false });

export function launch() {
  import('components/forms')
    .then(m => {
      m.initDatePickers();
    })
    .catch(error => showComponentError(error));

  // Validate file size
  const photoInput = document.querySelector('input[name=confirmation-photo]');
  FileAPI.event.on(photoInput, 'change', event => {
    photoInput.closest('.form-group').classList.remove('has-error');
    const files = FileAPI.getFiles(event);
    FileAPI.filterFiles(
      files,
      function (file, info) {
        if (/^image/.test(file.type)) {
          const mimeTypeSatisfied = photoRequirements.mimeTypes.includes(file.type);
          const minDimensionsSatisfied =
            info.width >= photoRequirements.minWidth && info.height >= photoRequirements.minHeight;
          const maxSizeRequirements = file.size < photoRequirements.maxFileSize * FileAPI.MB;
          return mimeTypeSatisfied && minDimensionsSatisfied && maxSizeRequirements;
        }
        return false;
      },
      function (list, other) {
        if (list.length === 0 && other.length > 0) {
          photoInput.closest('.form-group').classList.add('has-error');
        }
      }
    );
  });

  $('#confirm-email').click(throttledSubmitCode);
}
