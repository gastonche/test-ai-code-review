let age = 20;
let myAge = ++age;
console.log(myAge, "my age");
console.log(age, "age");
const size = 32;

// Data types
// Numbers
let num1 = 10;
let num2 = 10.5;
let sum = num1 + num2; // add numbers
let diff = num1 - num2; // subtract numbers
let product = num1 * num2; // multiply numbers
let quotient = num1 / num2; // divide numbers
let remainder = num1 % num2; // find remainder
num1 += 10; // num1 = num1+10
num1 -= 10; // num1 = num1-10
num1++;
num1--;
++num1;
num1 ** 4;

num1 = 10;
num2 = num1;
num1 = 20;
console.log(num1, num2);

// Strings
const str1 = "Hello World";
const str2 = "10";
const str3 = str1 + str2;
console.log(str3);
console.log(str1.length);

// Booleans
const bool1 = true;
const bool2 = false;
const bool3 = !bool1;
const bool4 = bool1 && bool2;
const bool5 = bool1 || bool2;

// Arrays
const arr1 = [1, 2, 3, 4, 5];
const arr2 = arr1;
arr1[1] = 10;
console.log(arr1, arr2, arr1[1]);
console.log({ arr1, arr2 });

// Objects
const person = {
  name: "John",
  age: 30,
  city: "New York",
  sex: "male",
  hobbies: ["reading", "running", "coding"],
};

const key = "name";
person.age += 31;
console.log(person, person.age, person[key], person["age"]);

num1 = 10;
num2 = "10";
console.log(num1 == num2);
console.log(num1 === num2);
