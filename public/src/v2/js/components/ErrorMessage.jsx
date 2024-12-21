import PropTypes from 'prop-types';
import React from 'react';

import { ErrorMessage as BaseErrorMessage } from '@hookform/error-message';

function ErrorMessage({ className = '', ...rest }) {
  return (
    <BaseErrorMessage
      render={({ messages, message }) => {
        let errors = message ? [message] : messages;
        return (
          errors && (
            <p className={`help-text error ${className}`}>
              {Object.entries(errors).map(([type, message]) => (
                <span key={type}>{message}</span>
              ))}
            </p>
          )
        );
      }}
      {...rest}
    />
  );
}

ErrorMessage.propTypes = {
  className: PropTypes.string
};

export default ErrorMessage;
