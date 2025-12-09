import $ from 'jquery';
import i18next from 'i18next';
import jqueryI18next from './jquery-i18next';

jqueryI18next.init(i18next, $, {});

window.i18next = window.i18next || i18next;
