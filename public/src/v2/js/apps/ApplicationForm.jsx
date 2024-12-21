import * as PropTypes from 'prop-types';
import React, { Fragment, useEffect, useReducer } from 'react';

import ky from 'ky';
import { useAsync } from 'react-async';
import { useForm } from 'react-hook-form';

import {
  Checkbox,
  CreatableSelect,
  ErrorMessage,
  InputField,
  MemoizedTextField,
  RadioGroup,
  RadioOption,
  Select,
  Tooltip
} from 'components';
import { optionStrType } from 'types/props';
import { showErrorNotification, showNotification } from 'utils';

// TODO: потестить isPending. Есть какой-то devtools для react-async

const Hint = ({ ...options }) => (
  <Tooltip {...options}>
    <span className="tooltip__icon _rounded">?</span>
  </Tooltip>
);

let openAuthPopup = function (url, nextURL = null) {
  if (nextURL !== null) {
    url += `?next=${nextURL}`;
  }
  const name = '';
  const settings = `height=600,width=700,left=100,top=100,resizable=yes,scrollbars=yes,toolbar=no,menubar=no,location=yes,directories=no,status=yes`;
  window.open(url, name, settings);
};

const submitForm = async (
  [endpoint, csrfToken, setState, payload],
  props,
  { signal }
) => {
  const response = await ky.post(endpoint, {
    headers: {
      'X-CSRFToken': csrfToken
    },
    throwHttpErrors: false,
    json: payload,
    signal: signal
  });
  if (!response.ok) {
    if (response.status === 400) {
      const data = response.json();
      let msg = '<h5>Анкета не была сохранена</h5>';
      if (
        Object.keys(data).length === 1 &&
        Object.prototype.hasOwnProperty.call(data, 'non_field_errors')
      ) {
        msg += data['non_field_errors'];
        showErrorNotification(msg);
      } else {
        msg += 'Одно или более полей пропущены или заполнены некорректно.';
        showNotification(msg, { type: 'error', timeout: 3000 });
      }
    } else if (response.status === 403) {
      let msg = '<h5>Анкета не была сохранена</h5>Приемная кампания окончена.';
      showErrorNotification(msg);
    } else {
      showErrorNotification('Что-то пошло не так. Попробуйте позже.');
    }
  } else {
    setState({ isFormSubmitted: true });
  }
};

const msgRequired = 'Это поле обязательно для заполнения';
const rules = {
  lastName: { required: msgRequired },
  firstName: { required: msgRequired },
  patronymic: null,
  email: { required: msgRequired },
  phone: { required: msgRequired },
  livingPlace: { required: msgRequired },
  stepikId: null,
  githubLogin: null,
  university: { required: msgRequired },
  faculty: { required: msgRequired },
  course: { required: msgRequired },
  hasJob: { required: msgRequired },
  position: null,
  workplace: null,
  experience: null,
  onlineEducationExperience: null,
  campaign: { required: msgRequired },
  preferredStudyPrograms: {
    required: msgRequired
  },
  motivation: { required: msgRequired },
  probability: { required: msgRequired },
  additionalInfo: null,
  whereDidYouLearn: {
    required: msgRequired
  },
  whereDidYouLearnOther: {
    required: msgRequired
  },
  agreement: { required: msgRequired }
};

function ApplicationForm({
  endpoint,
  csrfToken,
  authCompleteUrl,
  authBeginUrl,
  campaigns,
  universities,
  educationLevelOptions,
  studyProgramOptions,
  sourceOptions,
  initialState
}) {
  const initial = {
    ...initialState
  };

  const reducer = (state, newState) => ({ ...state, ...newState });
  const [state, setState] = useReducer(reducer, initial);
  const { isPending, run: runSubmit } = useAsync({ deferFn: submitForm });
  const {
    register,
    control,
    handleSubmit,
    setValue,
    trigger,
    formState: { errors },
    watch
  } = useForm({
    mode: 'onBlur',
    defaultValues: { agreement: false }
  });

  useEffect(() => {
    register('has_job', rules.hasJob);
    register('university', rules.university);
    register('campaign', rules.campaign);
    register('course', rules.course);
    register('agreement', rules.agreement);
  }, [register]);

  const [
    selectedCampaignId,
    hasJob,
    selectedStudyPrograms,
    whereDidYouLearn,
    agreementConfirmed
  ] = watch([
    'campaign',
    'has_job',
    'preferred_study_programs',
    'where_did_you_learn',
    'agreement'
  ]);

  let selectedCampaign = campaigns.find(
    obj => obj.id === parseInt(selectedCampaignId)
  );

  function handleInputChange(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;
    setValue(name, value);
    if (name === 'campaign') {
      setValue('preferred_study_programs', []);
    }
  }

  function handleSelectChange(option, name) {
    setValue(name, option);
    trigger(name);
  }

  useEffect(() => {
    // Yandex.Passport global handlers (postMessage could be broken in IE11-)
    window.accessYandexLoginSuccess = login => {
      setState({ isYandexPassportAccessAllowed: true });
      showNotification('Доступ успешно предоставлен', { type: 'success' });
    };
    window.accessYandexLoginError = function (msg) {
      showNotification(msg, { type: 'error' });
    };
  }, []);

  let handleAccessYandexLogin = event => {
    event.preventDefault();
    const { isYandexPassportAccessAllowed } = state;
    if (isYandexPassportAccessAllowed) {
      return false;
    }
    openAuthPopup(authBeginUrl, authCompleteUrl);
    return false;
  };

  function onSubmit(data) {
    let { has_job, course, university, ...payload } = data;
    payload['has_job'] = has_job === 'yes';
    payload['level_of_education'] = course && course.value;
    if (university) {
      if (university.__isNew__) {
        payload['university_other'] = university.value;
      } else {
        payload['university'] = university.value;
      }
    }
    runSubmit(endpoint, csrfToken, setState, payload);
  }

  const { isYandexPassportAccessAllowed, isFormSubmitted } = state;

  if (isFormSubmitted) {
    return (
      <>
        <h3>Заявка зарегистрирована</h3>
        Спасибо за интерес к обучению в CS центре.
        <br />
        В ближайшее время вам придёт письмо с дальнейшими инструкциями и ссылкой
        на тест для поступающих.
        <br />
        Если в течение суток письмо не пришло, поищите его в спаме. Если там
        нет, напишите на{' '}
        <a href="mailto:info@compscicenter.ru">info@compscicenter.ru</a> о своей
        проблеме. Не забудьте указать свои ФИО и email.
      </>
    );
  }

  return (
    <form className="ui form" onSubmit={handleSubmit(onSubmit)}>
      <fieldset>
        <h3>Личная информация</h3>
        <div className="row">
          <InputField
            name="last_name"
            control={control}
            rules={rules.lastName}
            label={'Фамилия'}
            wrapperClass="col-lg-4"
          />
          <InputField
            control={control}
            rules={rules.firstName}
            name="first_name"
            label={'Имя'}
            wrapperClass="col-lg-4"
          />
          <InputField
            control={control}
            rules={rules.patronymic}
            name="patronymic"
            label={'Отчество'}
            wrapperClass="col-lg-4"
          />
          <InputField
            control={control}
            rules={rules.email}
            name="email"
            type="email"
            label={'Электронная почта'}
            wrapperClass="col-lg-4"
          />
          <InputField
            control={control}
            rules={rules.phone}
            name="phone"
            label={'Контактный телефон'}
            wrapperClass="col-lg-4"
            placeholder="+7 (999) 1234567"
          />
          <InputField
            control={control}
            rules={rules.livingPlace}
            name="living_place"
            label={'В каком городе вы живёте?'}
            wrapperClass="col-lg-4"
            placeholder=""
          />
        </div>
      </fieldset>
      <fieldset>
        <h3>Аккаунты</h3>
        <div className="row">
          <InputField
            control={control}
            rules={rules.stepikId}
            name="stepic_id"
            label={'ID на stepik.org'}
            wrapperClass="col-lg-4"
            helpText={'https://stepik.org/users/xxxx, ID — это xxxx'}
            placeholder="ХХХХ"
          />
          <InputField
            control={control}
            rules={rules.githubLogin}
            name="github_login"
            label={'Логин на github.com'}
            wrapperClass="col-lg-4"
            helpText={'https://github.com/xxxx, логин — это xxxx'}
            placeholder="ХХХХ"
          />
          <div className="field col-lg-4 mb-2">
            <label>
              Доступ к данным на Яндексе&nbsp;
              <Hint
                html={
                  'Вступительный тест организован в системе Яндекс.Контест. Чтобы выдать права участника и затем сопоставить результаты с анкетами, нам нужно знать ваш логин на Яндексе без ошибок, учитывая все особенности, например, вход через социальные сети. Чтобы всё сработало, поделитесь с нами доступом к некоторым данным из вашего Яндекс.Паспорта: логин и ФИО.'
                }
              />
            </label>
            <div className="grouped inline">
              <Checkbox
                required
                label={
                  isYandexPassportAccessAllowed
                    ? 'Доступ разрешен'
                    : 'Разрешить доступ'
                }
                disabled={isYandexPassportAccessAllowed}
                checked={isYandexPassportAccessAllowed}
                onChange={() => {}}
                onClick={handleAccessYandexLogin}
              />
            </div>
          </div>
        </div>
      </fieldset>
      <fieldset>
        <h3>Образование и опыт</h3>
        <div className="row">
          <div className="field col-lg-4">
            <div className="ui select">
              <label htmlFor="">Вуз</label>
              <CreatableSelect
                required
                components={{
                  DropdownIndicator: null
                }}
                openMenuOnFocus={true}
                isClearable={true}
                onChange={handleSelectChange}
                onBlur={e => trigger('university')}
                name="university"
                placeholder=""
                options={universities}
                menuPortalTarget={document.body}
                errors={errors}
              />
            </div>
            <div className="help-text">
              Расскажите, где вы учитесь или учились
            </div>
            <ErrorMessage errors={errors} name={'university'} />
          </div>
          <InputField
            control={control}
            rules={rules.faculty}
            name="faculty"
            label={'Специальность'}
            wrapperClass="col-lg-4"
            helpText={'Факультет, специальность или кафедра'}
          />

          <div className="field col-lg-4">
            <div className="ui select">
              <label htmlFor="">Курс</label>
              <Select
                onChange={handleSelectChange}
                onBlur={e => trigger('course')}
                name="course"
                isClearable={false}
                placeholder="Выберите из списка"
                options={educationLevelOptions}
                menuPortalTarget={document.body}
                required
                errors={errors}
              />
              <ErrorMessage errors={errors} name={'course'} />
            </div>
          </div>
        </div>
        <div className="row">
          <div className="field col-lg-12">
            <label>Вы сейчас работаете?</label>
            <RadioGroup
              required
              name="has_job"
              className="inline pt-0"
              onChange={handleInputChange}
            >
              <RadioOption id="yes">Да</RadioOption>
              <RadioOption id="no">Нет</RadioOption>
            </RadioGroup>
          </div>
        </div>
        {hasJob && hasJob === 'yes' && (
          <div className="row ">
            <InputField
              control={control}
              rules={rules.position}
              name="position"
              label={'Должность'}
              wrapperClass="col-lg-4"
            />
            <InputField
              control={control}
              rules={rules.workplace}
              name="workplace"
              label={'Место работы'}
              wrapperClass="col-lg-4"
            />
          </div>
        )}
        <div className="row">
          <MemoizedTextField
            name="experience"
            control={control}
            rules={rules.experience}
            wrapperClass="col-lg-8"
            label="Расскажите об опыте программирования и исследований"
            helpText="Напишите здесь о том, что вы делаете на работе, и о своей нынешней дипломной или курсовой работе. Здесь стоит рассказать о студенческих проектах, в которых вы участвовали, или о небольших личных проектах, которые вы делаете дома, для своего удовольствия. Если хотите, укажите ссылки, где можно посмотреть текст или код работ."
          />
          <MemoizedTextField
            name="online_education_experience"
            control={control}
            rules={rules.onlineEducationExperience}
            wrapperClass="col-lg-8"
            label="Вы проходили какие-нибудь онлайн-курсы? Какие? Какие удалось закончить?"
            helpText="Приведите ссылки на курсы или их названия и платформы, где вы их проходили. Расскажите о возникших трудностях. Что понравилось, а что не понравилось в таком формате обучения?"
          />
        </div>
      </fieldset>
      <fieldset>
        <h3>CS центр</h3>
        <div className="row">
          <div className="field col-lg-12">
            <label>
              Выберите отделение, в котором собираетесь учиться&nbsp;
              <Hint
                interactive={true}
                html={
                  <>
                    <p>
                      Если вы живёте в Санкт-Петербурге или Новосибирске, мы
                      рассмотрим вашу анкету в конкурсе на очное обучение.
                    </p>
                    <p>
                      Жителям Екатеринбурга, Минска, Москвы и Нижнего Новгорода
                      рекомендуем поступать в{' '}
                      <a
                        href="https://yandexdataschool.ru/"
                        target="_blank"
                        style={{ color: '#07c39f' }}
                        rel="noreferrer noopener nofollow"
                      >
                        ШАД Яндекса
                      </a>{' '}
                      — в этих городах есть филиалы с очными занятиями.
                    </p>
                  </>
                }
              />
            </label>
            <RadioGroup
              required
              name="campaign"
              className="inline pt-0"
              onChange={handleInputChange}
            >
              {campaigns.map(branch => (
                <RadioOption
                  key={branch.id}
                  id={`campaign-${branch.value}`}
                  value={branch.id}
                >
                  {branch.label}
                </RadioOption>
              ))}
            </RadioGroup>
          </div>
        </div>
        {selectedCampaign && (
          <Fragment>
            <div className="row">
              <div className="field col-lg-8">
                <label>
                  Какие направления обучения из трех вам интересны в CS центре?
                </label>
                <p className="text-small mb-2">
                  Мы не просим поступающих сразу определиться с направлением
                  обучения. Вам предстоит сделать этот выбор через год-полтора
                  после поступления. Сейчас мы предлагаем указать одно или
                  несколько направлений, которые кажутся вам интересными.
                </p>
                <div className="grouped">
                  {studyProgramOptions.map(option => (
                    <Checkbox
                      key={option.value}
                      name="preferred_study_programs"
                      className={errors.preferred_study_programs ? 'error' : ''}
                      {...register(
                        'preferred_study_programs',
                        rules.preferredStudyPrograms
                      )}
                      value={option.value}
                      label={option.label}
                    />
                  ))}
                </div>
                <ErrorMessage
                  errors={errors}
                  name={'preferred_study_programs'}
                  className="mt-2"
                />
              </div>
            </div>
            {selectedStudyPrograms && selectedStudyPrograms.includes('cs') && (
              <div className="row">
                <div className="field col-lg-8">
                  <div className="ui input">
                    <label htmlFor="preferred_study_programs_cs_note">
                      Вы бы хотели заниматься исследованиями в области Computer
                      Science? Какие темы вам особенно интересны?
                    </label>
                    <p className="text-small mb-2">
                      Вы можете посмотреть список возможных тем и руководителей
                      НИРов у нас на{' '}
                      <a
                        target="_blank"
                        href="https://compscicenter.ru/projects/#research-curators"
                        rel="noopener noreferrer"
                      >
                        сайте
                      </a>
                      .
                    </p>
                    <textarea
                      id="preferred_study_programs_cs_note"
                      name="preferred_study_programs_cs_note"
                      rows="6"
                      {...register('preferred_study_programs_cs_note')}
                    />
                  </div>
                </div>
              </div>
            )}
            {selectedStudyPrograms && selectedStudyPrograms.includes('ds') && (
              <div className="row">
                <div className="field col-lg-8">
                  <div className="ui input">
                    <label htmlFor="preferred_study_programs_dm_note">
                      Что вам больше всего интересно в области Data Science?
                      Какие достижения последних лет вас особенно удивили?
                    </label>
                    <textarea
                      id="preferred_study_programs_dm_note"
                      name="preferred_study_programs_dm_note"
                      rows="6"
                      {...register('preferred_study_programs_dm_note')}
                    />
                  </div>
                </div>
              </div>
            )}
            {selectedStudyPrograms && selectedStudyPrograms.includes('se') && (
              <div className="row">
                <div className="field col-lg-8">
                  <div className="ui input">
                    <label htmlFor="preferred_study_programs_se_note">
                      В разработке какого приложения, которым вы пользуетесь
                      каждый день, вы хотели бы принять участие? Каких знаний
                      вам для этого не хватает?
                    </label>
                    <textarea
                      id="preferred_study_programs_se_note"
                      name="preferred_study_programs_se_note"
                      rows="6"
                      {...register('preferred_study_programs_se_note')}
                    />
                  </div>
                </div>
              </div>
            )}
            {selectedStudyPrograms &&
              selectedStudyPrograms.includes('robotics') && (
                <div className="row">
                  <div className="field col-lg-8">
                    <div className="ui input">
                      <label htmlFor="preferred_study_programs_se_note">
                        Какие направления применения роботов вы считаете
                        наиболее перспективными?
                      </label>
                      <textarea
                        id="preferred_study_programs_robotics_note"
                        name="preferred_study_programs_robotics_note"
                        rows="6"
                        {...register('preferred_study_programs_robotics_note')}
                      />
                    </div>
                  </div>
                </div>
              )}
          </Fragment>
        )}

        <div className="row">
          <MemoizedTextField
            name="motivation"
            control={control}
            rules={rules.motivation}
            wrapperClass="col-lg-8"
            label="Почему вы хотите учиться в CS центре? Что вы ожидаете от обучения?"
          />
          <MemoizedTextField
            name="probability"
            control={control}
            rules={rules.probability}
            label="Что нужно для выпуска из CS центра? Оцените вероятность, что вы сможете это сделать"
            wrapperClass="col-lg-8"
          />
          <MemoizedTextField
            name="additional_info"
            control={control}
            rules={rules.additionalInfo}
            wrapperClass="col-lg-8"
            label="Напишите любую дополнительную информацию о себе"
          />
        </div>
        <div className="row">
          <div className="field col-lg-8">
            <label className="mb-4">Откуда вы узнали о CS центре?</label>
            <div className="grouped">
              {sourceOptions.map(option => (
                <Checkbox
                  key={option.value}
                  name="where_did_you_learn"
                  {...register('where_did_you_learn', rules.whereDidYouLearn)}
                  value={option.value}
                  className={
                    errors && errors.where_did_you_learn ? 'error' : ''
                  }
                  label={option.label}
                />
              ))}
            </div>
            <ErrorMessage
              errors={errors}
              name={'where_did_you_learn'}
              className="mt-2"
            />
          </div>
          {whereDidYouLearn && whereDidYouLearn.includes('other') && (
            <InputField
              name="where_did_you_learn_other"
              control={control}
              rules={rules.whereDidYouLearnOther}
              wrapperClass="animation col-lg-5"
              placeholder="Ваш вариант"
            />
          )}
        </div>
      </fieldset>
      <div className="row">
        <div className="col-lg-12">
          <div className="grouped mb-4">
            <Checkbox
              required
              name={'agreement'}
              label={
                <>
                  Настоящим подтверждаю свое согласие на обработку Оператором
                  моих персональных данных в соответствии с{' '}
                  <a
                    target="_blank"
                    href="https://compscicenter.ru/policy/"
                    rel="noopener noreferrer"
                  >
                    Политикой в отношении обработки персональных данных
                    Пользователей Веб-сайта
                  </a>
                  , а также гарантирую достоверность представленных мной данных
                </>
              }
              onChange={handleInputChange}
            />
          </div>
          <button
            type="submit"
            disabled={!agreementConfirmed || isPending}
            className="btn _primary _m-wide"
          >
            Подать заявку
          </button>
        </div>
      </div>
    </form>
  );
}

ApplicationForm.propTypes = {
  initialState: PropTypes.shape({
    isYandexPassportAccessAllowed: PropTypes.bool.isRequired
  }).isRequired,
  endpoint: PropTypes.string.isRequired,
  csrfToken: PropTypes.string.isRequired,
  authBeginUrl: PropTypes.string.isRequired,
  authCompleteUrl: PropTypes.string.isRequired,
  campaigns: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      id: PropTypes.number.isRequired
    })
  ).isRequired,
  sourceOptions: PropTypes.arrayOf(optionStrType).isRequired,
  universities: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      label: PropTypes.string.isRequired
    })
  ).isRequired,
  educationLevelOptions: PropTypes.arrayOf(optionStrType).isRequired,
  studyProgramOptions: PropTypes.arrayOf(optionStrType).isRequired
};

export default ApplicationForm;
