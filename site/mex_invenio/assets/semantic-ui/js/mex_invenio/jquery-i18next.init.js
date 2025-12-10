/* global $ */

import i18next from 'i18next';
import { init as initJqueryI18next } from './jquery-i18next';

initJqueryI18next(i18next, $, {});

window.i18next = window.i18next || i18next;
