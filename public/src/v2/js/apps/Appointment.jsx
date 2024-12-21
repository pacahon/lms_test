import React, { useState } from 'react';
import '@cscenter/react-dates/initialize';
import PropTypes from 'prop-types';
import useFetch from 'use-http';
import { SingleDatePicker, isSameDay } from '@cscenter/react-dates';
import _uniqWith from 'lodash-es/uniqWith';
import { ICON_AFTER_POSITION } from '@cscenter/react-dates/lib/constants';
import '@cscenter/react-dates/lib/css/_datepicker.css';
import moment from 'moment';
import 'moment/locale/ru';
import cn from 'classnames';
import { showNotification, showErrorNotification } from '../utils';

moment.locale('ru');

const dateFormat = 'YYYY-MM-DD';

function Appointment({
  endpointSlotOccupation,
  endpointDeclineInvitation,
  invitationDeadline,
  csrfToken,
  days
}) {
  const [state, setState] = useState({
    date: null,
    slot: null,
    venue: null,
    isInvitationAccepted: false,
    isInvitationDeclined: false
  });
  const [showDeclineInvitation, setShowDeclineInvitation] = useState(false);
  const [focusedInput, setFocusedInput] = useState(false);
  const options = {
    onError: ({ error }) => {
      if (response.status >= 500 && response.status < 600) {
        showErrorNotification(`${response.statusText}. Try again later.`);
      } else {
        const messages = response.data.errors.map(error => error.message);
        showErrorNotification(messages.join('<br/>'));
      }
    },
    cacheLife: 0,
    cachePolicy: 'no-cache',
    headers: {
      'X-CSRFToken': csrfToken
    },
    timeout: 5000
  };
  // FIXME: Right now we use the same hook for accepting/declining invitation. Better design would be to implement separated components for this actions
  const { request, response } = useFetch('', options);
  const { date, slot } = state;

  const handleDateChange = date => {
    setState(prevState => ({ ...prevState, date, slot: null }));
  };

  const takeSlot = async () => {
    await request.post(endpointSlotOccupation.replace('{slotId}', slot.value));
    if (response.ok) {
      showNotification('Приглашение успешно принято.', { type: 'success' });
      setState(prevState => ({ ...prevState, isInvitationAccepted: true }));
    }
  };

  const declineInvitation = async () => {
    request.abort();
    await request.put(endpointDeclineInvitation);
    if (response.ok) {
      setState(prevState => ({ ...prevState, isInvitationDeclined: true }));
    }
  };

  let highlightedDays = days.map(day => moment(day.date, dateFormat, true));
  highlightedDays = _uniqWith(highlightedDays, isSameDay);
  const firstDay = highlightedDays.reduce((acc, current) => {
    return acc.isBefore(current) ? acc : current;
  });
  const lastDay = highlightedDays.reduce((acc, current) => {
    return acc.isAfter(current) ? acc : current;
  });

  const dateFormatted = date && date.format(dateFormat);
  const selectedDays = days.filter(({ date }) => date === dateFormatted);

  const canSubmit = date !== null && slot !== null;

  if (state.isInvitationAccepted) {
    return (
      <div id={'appointment__card'} className="card border-xs-0 grey-bg">
        <div className="card__header _big">
          <h2 className="mb-2">Ждём вас на собеседование</h2>
          <b>Дата и время</b>: {date.format('DD MMMM, dddd')}, в {slot.label}
          <br />
          <b>Место проведения</b>: {state.venue.address}
        </div>
      </div>
    );
  }

  if (showDeclineInvitation) {
    return (
      <>
        <div id={'appointment__card'} className="card border-xs-0 grey-bg">
          <div className="card__header _big">
            {!state.isInvitationDeclined && (
              <>
                <p>
                  Вы уверены, что ни один из выбранных слотов вам не подходит?
                  Если уверены, нажмите «Отклонить приглашение» — мы выберем
                  новые даты и пригласим вас ещё раз. Чтобы посмотреть варианты
                  времени ещё раз, нажмите «Назад».
                </p>
                <button
                  className="btn _big _primary"
                  onClick={() => {
                    !request.loading && declineInvitation();
                  }}
                >
                  Отклонить приглашение
                </button>
                <button
                  className="btn _big"
                  onClick={() => {
                    request.abort();
                    setShowDeclineInvitation(false);
                  }}
                >
                  Назад
                </button>
              </>
            )}
            {state.isInvitationDeclined && (
              <h2 className="mb-0">Приглашение отклонено</h2>
            )}
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <div id={'appointment__card'} className="card border-xs-0 grey-bg">
        <div className="card__header _big pb-0">
          <h2 className="mb-2">Приглашаем вас на собеседование</h2>
          Выберите дату и время из доступных вариантов.
          <br />
          Приглашение будет актуально до {invitationDeadline} по московскому
          времени.
        </div>
        <div className="card__content _big">
          <SingleDatePicker
            id="date_input"
            date={date}
            minDate={firstDay}
            maxDate={lastDay}
            initialVisibleMonth={() => firstDay}
            isOutsideRange={day =>
              !highlightedDays.some(day2 => {
                return isSameDay(day, day2);
              })
            }
            isDayHighlighted={day1 =>
              highlightedDays.some(day2 => {
                return isSameDay(day1, day2);
              })
            }
            onDateChange={handleDateChange}
            showDefaultInputIcon={true}
            placeholder={'Дата собеседования'}
            focused={focusedInput}
            onFocusChange={({ focused }) => setFocusedInput(focused)}
            numberOfMonths={1}
            inputIconPosition={ICON_AFTER_POSITION}
            hideKeyboardShortcutsPanel={true}
            displayFormat={() => moment.localeData().longDateFormat('LL')}
            transitionDuration={0}
          />
          <br />
          <a
            href="#"
            className="_dashed d-inline-block mt-1"
            onClick={() => {
              request.abort();
              setShowDeclineInvitation(true);
            }}
          >
            Нет подходящего времени?
          </a>
          {selectedDays.length > 0 && (
            <>
              {selectedDays.map(selectedDay => (
                <div className="mt-8" key={`day_${selectedDay.id}`}>
                  <h4>
                    <b>Место проведения</b>: {selectedDay.venue.address}
                  </h4>
                  {selectedDay.section.value !== 'all_in_1' && (
                    <h4>
                      <b>Секция</b>: {selectedDay.section.label}
                    </h4>
                  )}
                  <div className="appointment-slots flex-gap">
                    {selectedDay.slots.map(s => {
                      return (
                        <label
                          className={cn({
                            'btn _small _outline slot': true,
                            slot__disabled: !s.available,
                            slot__selected: slot && slot.value === s.value
                          })}
                          key={`day_${s.value}`}
                          onClick={() =>
                            s.available &&
                            setState(prevState => ({
                              ...prevState,
                              slot: s,
                              venue: selectedDay.venue
                            }))
                          }
                        >
                          <input
                            type="radio"
                            name="time"
                            autoComplete="off"
                            value={s.value}
                          />
                          {s.label}
                        </label>
                      );
                    })}
                  </div>
                </div>
              ))}
            </>
          )}
          {canSubmit && (
            <>
              <hr className="my-8" />
              <h3>Проверьте данные</h3>
              <b>Дата и время</b>: {date.format('DD MMMM, dddd')}, в {slot.label}
              <br />
              <b>Место проведения</b>: {state.venue.address}
            </>
          )}
        </div>
        <div className="card__content _big _meta">
          <button
            disabled={!canSubmit}
            className="btn _big _primary"
            onClick={() => {
              !request.loading && takeSlot();
            }}
          >
            Записаться
          </button>
        </div>
      </div>
    </>
  );
}

Appointment.propTypes = {
  endpointSlotOccupation: PropTypes.string.isRequired,
  endpointDeclineInvitation: PropTypes.string.isRequired,
  invitationDeadline: PropTypes.string.isRequired,
  csrfToken: PropTypes.string.isRequired,
  days: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      date: PropTypes.string.isRequired,
      format: PropTypes.string.isRequired,
      section: PropTypes.shape({
        value: PropTypes.string.isRequired,
        label: PropTypes.string.isRequired
      }),
      venue: PropTypes.shape({
        name: PropTypes.string.isRequired,
        address: PropTypes.string.isRequired,
        description: PropTypes.string.isRequired
      }),
      slots: PropTypes.arrayOf(
        PropTypes.shape({
          value: PropTypes.number.isRequired,
          label: PropTypes.string.isRequired,
          available: PropTypes.bool.isRequired
        })
      )
    })
  ).isRequired
};

export default Appointment;
