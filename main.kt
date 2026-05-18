fun main() {
    val num1 = 15.0
    val num2 = 5.0
    
    println("Numbers: $num1 and $num2")
    println("------------------------")
    println("Sum:      ${sum(num1, num2)}")
    println("Subtract: ${subtract(num1, num2)}")
    println("Multiply: ${multiply(num1, num2)}")
    println("Divide:   ${divide(num1, num2)}")
    
    // Testing division by zero
    println("Divide by zero: ${divide(num1, 0.0)}")
}

// Function to add two numbers
fun sum(a: Double, b: Double): Double {
    return a + b
}

// Function to subtract the second number from the first
fun subtract(a: Double, b: Double): Double {
    return a - b
}

// Function to multiply two numbers
fun multiply(a: Double, b: Double): Double {
    return a * b
}

// Function to divide the first number by the second
// Includes a check to avoid division by zero
fun divide(a: Double, b: Double): Double {
    if (b == 0.0) {
        println("Error: Division by zero is not allowed.")
        return Double.NaN // Returns "Not a Number"
    }
    return a / b
}
