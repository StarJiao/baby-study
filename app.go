package main

import (
	"context"
	"fmt"
	"math/rand"
	"time"
)

// Question represents a math question
type Question struct {
	Expression string `json:"expression"`
	Answer     int    `json:"answer"`
}

// App struct
type App struct {
	ctx context.Context
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{}
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}

// Greet returns a greeting for the given name
func (a *App) Greet(name string) string {
	return fmt.Sprintf("Hello %s, It's show time!", name)
}

// GenerateQuestions generates math questions based on difficulty
func (a *App) GenerateQuestions(difficulty, count int) []Question {
	rand.Seed(time.Now().UnixNano())
	
	questions := make([]Question, 0, count)
	generated := make(map[string]bool)
	
	for len(questions) < count {
		q := generateSingleQuestion(difficulty)
		key := q.Expression
		
		if !generated[key] {
			generated[key] = true
			questions = append(questions, q)
		}
	}
	
	return questions
}

func generateSingleQuestion(difficulty int) Question {
	switch difficulty {
	case 1:
		return generateLevel1()
	case 2:
		return generateLevel2()
	case 3:
		return generateLevel3()
	case 4:
		return generateLevel4()
	default:
		return generateLevel1()
	}
}

// Level 1: 10以内加减
func generateLevel1() Question {
	a := rand.Intn(10)
	b := rand.Intn(10)
	isAdd := rand.Intn(2) == 0
	
	if isAdd {
		return Question{
			Expression: fmt.Sprintf("%d + %d", a, b),
			Answer:     a + b,
		}
	}
	// 确保结果是负数
	if a < b {
		a, b = b, a
	}
	return Question{
		Expression: fmt.Sprintf("%d - %d", a, b),
		Answer:     a - b,
	}
}

// Level 2: 10以内连加连减混合
func generateLevel2() Question {
	a := rand.Intn(8) + 1
	b := rand.Intn(8) + 1
	c := rand.Intn(8) + 1
	
	// 随机选择运算顺序: (a op1 b) op2 c
	op1 := []string{"+", "-"}[rand.Intn(2)]
	op2 := []string{"+", "-"}[rand.Intn(2)]
	
	var result int
	if op1 == "+" {
		result = a + b
	} else {
		result = a - b
	}
	
	// 确保最终结果非负
	if op2 == "+" {
		result = result + c
	} else {
		if result < c {
			// 调整c使其不会让结果为负
			c = result
		}
		result = result - c
	}
	
	// 重新生成确保结果在10以内
	for result > 10 || result < 0 {
		return generateLevel2()
	}
	
	return Question{
		Expression: fmt.Sprintf("%d %s %d %s %d", a, op1, b, op2, c),
		Answer:     result,
	}
}

// Level 3: 20以内无需借位进位
func generateLevel3() Question {
	isAdd := rand.Intn(2) == 0

	if isAdd {
		// 不进位加法: 11+8, 12+7 等（和不超过20，个位相加<=9）
		a := rand.Intn(10) + 11 // 11-20
		b := rand.Intn(9 - (a % 10)) + 1 // 1到(9-个位)的范围
		return Question{
			Expression: fmt.Sprintf("%d + %d", a, b),
			Answer:     a + b,
		}
	}
	// 不借位减法: 18-5, 16-3 等（个位够减）
	a := rand.Intn(10) + 11 // 11-20
	b := rand.Intn(a%10) + 1 // 1到个位的范围
	return Question{
		Expression: fmt.Sprintf("%d - %d", a, b),
		Answer:     a - b,
	}
}

// Level 4: 20以内需要借位进位
func generateLevel4() Question {
	isAdd := rand.Intn(2) == 0

	if isAdd {
		// 进位加法: 9+8, 8+7, 9+6 等（个位相加>=10）
		a := rand.Intn(5) + 6  // 6-10
		b := rand.Intn(10-a) + (10-a) % 5 + 4 // 确保进位
		if a+b < 10 {
			b = 10 - a + rand.Intn(5)
		}
		if a > 10 {
			a = rand.Intn(5) + 6
		}
		if b > 10 {
			b = rand.Intn(5) + 6
		}
		for a+b < 10 {
			a = rand.Intn(5) + 6
			b = rand.Intn(5) + 6
		}
		// 限制在20以内
		for a+b > 20 {
			a = rand.Intn(5) + 5
			b = rand.Intn(15-a) + 1
		}
		return Question{
			Expression: fmt.Sprintf("%d + %d", a, b),
			Answer:     a + b,
		}
	}
	// 借位减法: 12-8, 13-7, 14-9 等（个位不够减）
	// 随机选一个结果11-19
	result := rand.Intn(9) + 11
	// 随机选一个个位比结果个位大的减数
	unitsDigit := result % 10
	b := rand.Intn(9-unitsDigit) + unitsDigit + 1 // 至少比result的个位大1
	a := result + b // 这样 a - b = result，但需要借位
	return Question{
		Expression: fmt.Sprintf("%d - %d", a, b),
		Answer:     a - b,
	}
}
