const mathGrades = [90, 80, 70, 60, 50, 40, 30, 20, 10];
const physicsGrades = [90, 80, 70, 60, 50, 40, 30, 20, 10];
const chemistryGrades = [90, 80, 70, 60, 50, 40, 30, 20, 10];
const englishGrades = [90, 80, 70, 60, 50, 40, 30, 20, 10];

function getLargestGrade(grades, shouldPrintToConsole) {
  let largest = grades[0];
  for (let i = 1; i < grades.length; i++) {
    if (grades[i] > largest) {
      largest = grades[i];
    }
  }

  if(shouldPrintToConsole) {
    console.log("The largest grade is", largest);
  }

  return largest;
}

function addNumbers(num1, num2=num1) {
  return num1 + num2;
}

console.log(addNumbers(10));

const largestMath = getLargestGrade(mathGrades, true);
const largestPhysics = getLargestGrade(physicsGrades);
const largestChemistry = getLargestGrade(chemistryGrades);
const largestEnglish = getLargestGrade(true, englishGrades);

console.log(largestMath, largestPhysics, largestChemistry, largestEnglish);

function getAverage(grades) {
  let sum = 0;
  for (let i = 0; i < grades.length; i++) {
    sum += grades[i];
  }
  return sum / grades.length;
}
