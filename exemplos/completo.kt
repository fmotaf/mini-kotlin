fun calcular(x: Int, y: Int)
  var resultado = x + y
  while resultado > 0
    println(resultado)
    resultado = resultado - 1
  return resultado

fun avaliar(valor: Int)
  if valor > 10
    println("grande")
  else
    println("pequeno")

fun main()
  val a = 15
  val b = 5
  val total = calcular(a, b)
  avaliar(total)
