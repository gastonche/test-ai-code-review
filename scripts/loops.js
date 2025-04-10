// While loop
// const number = Math.floor(Math.random() * 100);

// console.log(number);

// let guess = prompt("Guess a number between 1 and 100");

// while (guess != number) {
//   guess = prompt("Your guess is not correct. Guess a number between 1 and 100");
// }

// alert("You guessed it right! the number is " + number);

/*
For loop
*/

const namesOfStudents = ["John", "Mary", "David", "Sarah", "Michael", "Lisa", "Anna"];

for (let i = namesOfStudents.length - 1; i >= 0; i--) {
  console.log(namesOfStudents[i]);
} 

for(let i in namesOfStudents) {
  console.log("Student name: " + namesOfStudents[i]);
}

for (let i of namesOfStudents) {
  console.log(i);
  let name  = i;
  console.log(name, "name here");
  let age = i.length;
  console.log("Age is", age);
}

console.log("name is", name);
console.log("The age is", age);

if(age <= 1) {
  console.log("The student is a child");
} else if(age < 5) {

}