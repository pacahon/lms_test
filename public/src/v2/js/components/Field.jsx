import PropTypes from 'prop-types';
import React from 'react';

import cn from 'classnames';
import { useController } from 'react-hook-form';

import { ErrorMessage, Input, Hint } from 'components';

export function InputField({
  name,
  control,
  rules = null,
  defaultValue = '',
  label = null,
  className = null,
  wrapperClass = null,
  helpText = null,
  hint = null,
  ...rest
}) {
  const { field, fieldState } = useController({
    name,
    control,
    rules,
    defaultValue,
    // Note: Will trigger re-render for conditional fields
    shouldUnregister: true
  });
  return (
    <div
      className={cn({
        field: true,
        [wrapperClass]: wrapperClass !== null
      })}
    >
      {label !== null && (
        <label htmlFor={name}>
            {label}
            &nbsp;
            {hint !== null && (
                <Hint interactive={true} html={hint}/>
            )}
        </label>
        )}
      <Input
        name={name}
        id={name}
        className={cn({
          [className]: className !== null,
          error: fieldState.error
        })}
        {...rest}
        {...field}
      />
      {helpText !== null && <div className="help-text">{helpText}</div>}
      <ErrorMessage errors={{ [name]: fieldState.error }} name={name} />
    </div>
  );
}

const fieldProps = {
  name: PropTypes.string.isRequired,
  control: PropTypes.object.isRequired,
  rules: PropTypes.object,
  defaultValue: PropTypes.string,
  className: PropTypes.string,
  label: PropTypes.string,
  helpText: PropTypes.string,
  hint: PropTypes.string,
  wrapperClass: PropTypes.string
};

InputField.propTypes = fieldProps;

export function TextField({
  name,
  control,
  rules = null,
  defaultValue = '',
  label = null,
  className = null,
  wrapperClass = null,
  helpText = null,
  ...rest
}) {
  const { field, fieldState } = useController({
    name,
    control,
    rules,
    defaultValue,
    shouldUnregister: true
  });

  return (
    <div
      className={cn({
        field: true,
        [wrapperClass]: wrapperClass !== null
      })}
    >
      {label !== null && <label htmlFor={name}>{label}</label>}
      {helpText !== null && <div className="text-small mb-2">{helpText}</div>}
      <div
        className={cn({
          'ui input': true,
          error: fieldState.error
        })}
      >
        <textarea name={name} id={name} rows="6" {...field} {...rest} />
      </div>
      <ErrorMessage errors={{ [name]: fieldState.error }} name={name} />
    </div>
  );
}

TextField.propTypes = fieldProps;

export const MemoizedInputField = React.memo(InputField);

export const MemoizedTextField = React.memo(TextField);
