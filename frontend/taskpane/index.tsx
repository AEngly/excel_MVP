import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { App } from './components/App';

Office.onReady(() => {
  ReactDOM.render(<App />, document.getElementById('root'));
});
