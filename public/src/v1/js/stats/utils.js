import i18n from './i18n';

import template from 'lodash-es/template';

export const GROUPS = {
  1: i18n.groups.STUDENT_CENTER,
  4: i18n.groups.VOLUNTEER,
  3: i18n.groups.GRADUATE_CENTER
};

export const StudentTypes = {
  regular: i18n.studentTypes.REGULAR,
  invited: i18n.studentTypes.INVITED,
  graduate: i18n.studentTypes.GRADUATE
};

export const COLOR_PALETTE = ['#5cb85c', '#f96868', '#F6BE80', '#515492', '#4F86A0'];

export const URLS = window.URLS;

export function getTemplate(id) {
  return template(document.getElementById(id).innerHTML);
}

export function getStudentType(studentProfile) {
  // Graduate is actually a status and it's inconsistent since it
  // changes state after student graduation
  const value = studentProfile.status === 'graduate' ? studentProfile.status : studentProfile.type;
  const label = Object.prototype.hasOwnProperty.call(StudentTypes, value)
    ? StudentTypes[value]
    : 'Unknown Type';
  return { value, label };
}
