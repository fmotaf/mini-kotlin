fun calcular(x: Int, y: Int)
  var resultado = x + y
  while resultado > 0
    println(resultado)
    resultado = resultado - 1
  return resultado

fun main()
  val a = 15.0
  val b = 5.0
  println(calcular(a, b))
