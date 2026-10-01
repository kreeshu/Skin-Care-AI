/**
 * SkinCare AI - participant usability survey (CMP6200 FYP).
 *
 * How to use:
 *   1. Open https://script.google.com, create a new project, paste this file.
 *   2. Click Run on createSkinCareSurvey and accept the permission prompt.
 *   3. The execution log prints the edit link and the public link to share.
 *   4. After collecting responses: Form > Responses > Download responses (.csv),
 *      then run analyse_sus.py on that CSV.
 *
 * The form collects no names, emails or photos.
 */
var TASKS = [
  'Task 1 - Check a face photo (tap "+" in Chat and choose a photo)',
  'Task 2 - Open the result and read what each concern means',
  'Task 3 - Find a recommended product and save it to your shelf',
  'Task 4 - Ask the assistant one question about your result'
];

var SUS_ITEMS = [
  'I think that I would like to use this app frequently.',
  'I found the app unnecessarily complex.',
  'I thought the app was easy to use.',
  'I think that I would need the support of a technical person to be able to use this app.',
  'I found the various functions in this app were well integrated.',
  'I thought there was too much inconsistency in this app.',
  'I would imagine that most people would learn to use this app very quickly.',
  'I found the app very cumbersome to use.',
  'I felt very confident using the app.',
  'I needed to learn a lot of things before I could get going with this app.'
];

function createSkinCareSurvey() {
  var form = FormApp.create('SkinCare AI - Usability Survey');
  form.setDescription(
    'Thank you for testing SkinCare AI, a final-year university project. ' +
    'The app looks at a face photo, reports visible cosmetic skin concerns and suggests ' +
    'products sold in Nepal. It is NOT a medical tool.\n\n' +
    'The survey takes about 10 minutes. It is anonymous: no names, emails or photos are collected.');
  form.setCollectEmail(false);
  form.setLimitOneResponsePerUser(false);
  form.setProgressBar(true);
  form.setShowLinkToRespondAgain(false);

  // 1. Information and consent
  form.addSectionHeaderItem().setTitle('1. Information and consent').setHelpText(
    'Taking part is voluntary and you may stop at any time without giving a reason. ' +
    'Any photo you use in the app is analysed in memory and is not stored. ' +
    'Your answers are anonymous and will be used only in the project report. ' +
    'The app gives cosmetic observations, not medical advice.');
  form.addMultipleChoiceItem()
    .setTitle('I have read the information above, I am 18 or older, and I agree to take part.')
    .setChoiceValues(['Yes, I agree'])
    .setRequired(true);

  // 2. About you
  form.addPageBreakItem().setTitle('2. About you');
  form.addMultipleChoiceItem().setTitle('Age group')
    .setChoiceValues(['18-24', '25-34', '35-44', '45 or older', 'Prefer not to say']).setRequired(true);
  form.addMultipleChoiceItem().setTitle('How would you describe your skin type?')
    .setChoiceValues(['Dry', 'Normal', 'Oily', 'Combination', 'Sensitive', 'Not sure']).setRequired(true);
  form.addMultipleChoiceItem().setTitle('Have you used a skincare or beauty app before?')
    .setChoiceValues(['Yes, often', 'Yes, once or twice', 'No']).setRequired(true);
  form.addMultipleChoiceItem().setTitle('Which photo did you use in the app?')
    .setChoiceValues(['My own photo', 'A sample photo provided by the researcher']).setRequired(true);

  // 3. Tasks
  form.addPageBreakItem().setTitle('3. Tasks').setHelpText(
    'Please try each task in the app, then answer the two questions for it.');
  TASKS.forEach(function (task) {
    form.addMultipleChoiceItem().setTitle(task + ': did you complete it?')
      .setChoiceValues(['Yes, without help', 'Yes, with some help', 'No']).setRequired(true);
    form.addScaleItem().setTitle(task + ': how easy was it?')
      .setBounds(1, 5).setLabels('Very difficult', 'Very easy').setRequired(true);
  });

  // 4. System Usability Scale
  form.addPageBreakItem().setTitle('4. Overall usability (System Usability Scale)').setHelpText(
    'Rate each statement from 1 (strongly disagree) to 5 (strongly agree).');
  SUS_ITEMS.forEach(function (item, i) {
    form.addScaleItem().setTitle('SUS' + (i + 1) + '. ' + item)
      .setBounds(1, 5).setLabels('Strongly disagree', 'Strongly agree').setRequired(true);
  });

  // 5. Understanding and trust
  form.addPageBreakItem().setTitle('5. Understanding and trust');
  form.addMultipleChoiceItem()
    .setTitle('When a concern is marked "uncertain", what does it mean?')
    .setChoiceValues([
      'The app is not confident whether the concern is visible',
      'The concern is serious and needs a doctor',
      'The photo was rejected',
      'I am not sure'])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle('Did you notice the message saying the app does not give medical advice?')
    .setChoiceValues(['Yes', 'No']).setRequired(true);
  form.addScaleItem().setTitle('The results matched what I can see on my (or the sample) skin.')
    .setBounds(1, 5).setLabels('Strongly disagree', 'Strongly agree').setRequired(true);
  form.addScaleItem().setTitle('I trust the product recommendations.')
    .setBounds(1, 5).setLabels('Strongly disagree', 'Strongly agree').setRequired(true);
  form.addScaleItem().setTitle('The reasons shown for each product (matched ingredients) were helpful.')
    .setBounds(1, 5).setLabels('Strongly disagree', 'Strongly agree').setRequired(true);
  form.addScaleItem().setTitle('I would consider buying a recommended product.')
    .setBounds(1, 5).setLabels('Strongly disagree', 'Strongly agree').setRequired(true);

  // 6. Comments
  form.addPageBreakItem().setTitle('6. Your comments');
  form.addParagraphTextItem().setTitle('What did you like most about the app?');
  form.addParagraphTextItem().setTitle('What was confusing or should be improved?');

  form.setConfirmationMessage('Thank you for taking part!');
  Logger.log('Edit link:  ' + form.getEditUrl());
  Logger.log('Share link: ' + form.getPublishedUrl());
}
