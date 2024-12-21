import _debounce from 'lodash-es/debounce';

const ENTRY_POINT = $('.user-search #ajax-uri').val();
let queryName = '';
let branches = {};
let curriculumYears = {};
let admissionYears = {};
let studentTypes = {};
let status = {};
let passedCoursesTotal = {};
let academicDisciplines = {};
let partners = {};
let isPaidBasis = {};
let UniGraduationYear = {};

function getSelectedValues(items) {
  return Object.keys(items)
    .filter(key => items[key])
    .join(',');
}

function makeQuery() {
  let filters = {
    name: queryName,
    branches: getSelectedValues(branches),
    year_of_curriculum: getSelectedValues(curriculumYears),
    year_of_admission: getSelectedValues(admissionYears),
    types: getSelectedValues(studentTypes),
    status: getSelectedValues(status),
    cnt_enrollments: getSelectedValues(passedCoursesTotal),
    academic_disciplines: getSelectedValues(academicDisciplines),
    partners: getSelectedValues(partners),
    is_paid_basis: getSelectedValues(isPaidBasis),
    uni_graduation_year: getSelectedValues(UniGraduationYear)
  };

  $.ajax({
    url: ENTRY_POINT,
    data: filters,
    dataType: 'json',
    traditional: true
  })
    .done(function (data) {
      let found;
      if (data.next !== null) {
        found = `Показано: 500 из ${data.count}`;
      } else {
        found = `Найдено: ${data.count}`;
      }
      if (parseInt(data.count) > 0) {
        found += ` <a target="_blank" href="/staff/student-search.csv?${$.param(
          filters
        )}">скачать csv</a>`;
      }
      $('#user-num-container').html(found).show();
      let h = "<table class='table table-condensed'>";
      data.results.map(studentProfile => {
        h += `<tr><td>`;
        h += `<a href="/users/${studentProfile.user_id}/">${studentProfile.short_name}</a>`;
        h += '</td></tr>';
      });
      h += '</table>';
      $('#user-table-container').html(h);
    })
    .fail(function (jqXHR) {
      $('#user-num-container').html(`Найдено: 0`).show();
      $('#user-table-container').html(`Ошибка запроса:<code>${jqXHR.responseText}</code>`);
    });
}

const fn = {
  launch: function () {
    const query = _debounce(makeQuery, 200);

    $('.user-search')
      .on('keydown', function (e) {
        // Supress Enter
        if (e.keyCode === 13) {
          e.preventDefault();
        }
      })
      .on('input paste', '#name', function (e) {
        queryName = $(this).val();
        query();
      })
      .on('change', '[name="branches"]', function (e) {
        branches[$(this).val()] = this.checked;
        query();
      })
      .on('change', '[name="year_of_curriculum"]', function (e) {
        curriculumYears[$(this).val()] = this.checked;
        query();
      })
      .on('change', '[name="year_of_admission"]', function (e) {
        admissionYears[$(this).val()] = this.checked;
        query();
      })
      .on('change', '[name="type"]', function (e) {
        studentTypes[$(this).val()] = this.checked;
        query();
      })
      .on('change', '[name="status"]', function (e) {
        status[$(this).val()] = this.checked;
        query();
      })
      .on('change', '[name="academic_disciplines"]', function (e) {
        academicDisciplines[$(this).val()] = this.checked;
        query();
      })
      .on('change', '[name="partners"]', function (e) {
        partners[$(this).val()] = this.checked;
        query();
      })
      .on('change', '[name="cnt_enrollments"]', function (e) {
        passedCoursesTotal[$(this).val()] = this.checked;
        query();
      })
      .on('change', '[name="is_paid_basis"]', function (e) {
        isPaidBasis[$(this).val()] = this.checked;
        query();
      })
      .on('change', '[name="uni_graduation_year"]', function (e) {
        UniGraduationYear[$(this).val()] = this.checked;
        query();
      });
  }
};

$(function () {
  fn.launch();
});
