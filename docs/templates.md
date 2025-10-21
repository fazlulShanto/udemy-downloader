# Template System

The Udemy Downloader includes a sophisticated template system for rendering different types of course content as interactive HTML files. This system handles articles, quizzes, and coding assignments with responsive design and interactive functionality.

## Template Architecture

### Template Location
All templates are stored in the `templates/` directory:
```
templates/
├── article_template.html
├── quiz_template.html
└── coding_assignment_template.html
```

### Template Processing Flow
1. **Data Extraction**: Content data extracted from Udemy API
2. **Template Loading**: Appropriate template loaded based on content type
3. **Data Injection**: Content data injected into template placeholders
4. **File Generation**: Final HTML file written to course directory

## Article Template

### Purpose
Renders article-type lectures as formatted HTML documents with proper styling and layout.

### Template Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>__title_placeholder__</title>
    <!-- CSS styles embedded -->
</head>
<body>
    <div class="container">
        <div class="content">
            <div class="heading">__title_placeholder__</div>
            <div class="article-asset-container">__data_placeholder__</div>
        </div>
    </div>
</body>
</html>
```

### Placeholders
- `__title_placeholder__`: Article title (used twice - in title tag and heading)
- `__data_placeholder__`: Article HTML content body

### Styling Features
```css
/* Key styling components */
.container {
    position: relative;
    height: 100%;
    overflow-y: auto;
}

.content {
    padding: 3.2rem 4.8rem;
    word-break: break-word;
    max-width: 69.6rem;
    margin: 0 auto;
}

.heading {
    margin-bottom: 24px;
    font-family: -apple-system, BlinkMacSystemFont, Roboto, "Segoe UI", Helvetica, Arial, sans-serif;
    font-weight: 700;
    line-height: 1.2;
    font-size: 32px;
}

code {
    background-color: #fff;
    border: 1px solid #d1d7dc;
    color: #b4690e;
    font-size: 80%;
    padding: 0.2rem 0.4rem;
    font-family: sfmono-regular, Consolas, liberation mono, Menlo, Courier, monospace;
}
```

### Processing Function
```python
def process_article_template(lecture_title, body_content):
    """
    Process article template with content data.
    
    Args:
        lecture_title (str): Title of the article lecture
        body_content (str): HTML content body from Udemy API
        
    Process:
        1. Load article_template.html
        2. Replace __title_placeholder__ with lecture title
        3. Replace __data_placeholder__ with body content
        4. Write final HTML to course directory
        
    Output:
        HTML file with lecture title as filename in chapter directory
    """
```

## Quiz Template

### Purpose
Creates interactive quiz interfaces with multiple choice questions, explanations, and scoring functionality.

### Template Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Quiz</title>
    <!-- Extensive CSS for interactive elements -->
</head>
<body onload="main()">
    <main>
        <section id="quiz-meta-container">
            <h1 id="quiz-title"></h1>
            <p id="quiz-description"></p>
        </section>
        
        <section id="score-stats-container">
            <!-- Score tracking display -->
        </section>
        
        <section id="quiz-container">
            <!-- Dynamic quiz content -->
        </section>
        
        <dialog id="modal" class="modal-container">
            <!-- Explanation modal -->
        </dialog>
    </main>
    
    <script>
        const quizData = __data_placeholder__;
        // Interactive JavaScript functionality
    </script>
</body>
</html>
```

### Data Structure
```javascript
const quizData = {
    quiz_title: "Quiz Title",
    quiz_description: "Quiz description text",
    quiz_id: "quiz_identifier",
    pass_percent: 80,
    questions: [
        {
            id: "question_id",
            prompt: {
                question: "Question text",
                answers: ["Option A", "Option B", "Option C", "Option D"],
                explanation: "Explanation text"
            },
            correct_response: ["A"]  // Correct answer indicator
        }
        // ... more questions
    ]
};
```

### Interactive Features

#### Score Tracking
```javascript
function updateScore() {
    const currentParcentageElement = document.getElementById("current-score");
    const correctAnswerElement = document.getElementById("correct-answers");
    const wrongAnswerElement = document.getElementById("wrong-answers");
    
    correctAnswerElement.innerHTML = correct.size;
    wrongAnswerElement.innerHTML = incorrect.size;
    
    const score = Number((correct.size / totalNumberOfQuestions) * 100).toFixed(2);
    currentParcentageElement.innerHTML = score;
}
```

#### Question Rendering
```javascript
function renderSingleQuestion(singleQuestionData, rootIndex) {
    const { id, explanation, answers, correctAnswer, question } = singleQuestionData;
    
    // Shuffle answers for randomization
    for (let i = answers.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [answers[i], answers[j]] = [answers[j], answers[i]];
    }
    
    // Generate HTML for question and options
    const optionsHTML = answers.map((option, index) => {
        const optionId = `${id}_${index}`;
        return `
            <div class="question-lable">
                <input type="radio" id="${optionId}" name="answer" value="${option}" />
                <label for="${optionId}">${option}</label>
            </div>
        `;
    }).join("");
    
    // Create complete question container
    // ... HTML generation code
}
```

#### Answer Validation
```javascript
const submitButtonListener = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const selectedOption = e.target.querySelector('input[type="radio"]:checked');
    
    if (!selectedOption) {
        alert("Please select an answer!");
        return;
    }
    
    const { answer: userAnswer } = Object.fromEntries(formData.entries());
    const correctAnswer = e.target.dataset.correctAnswer;
    const questionId = e.target.dataset.questionId;
    
    let isCorrect = false;
    if (userAnswer == correctAnswer) {
        correct.add(questionId);
        incorrect.delete(questionId);
        isCorrect = true;
    } else {
        incorrect.add(questionId);
        correct.delete(questionId);
    }
    
    updateScore();
    
    // Visual feedback
    const resultClass = isCorrect ? "correct-answer" : "incorrect-answer";
    selectedOption.closest(".question-lable").classList.add(resultClass);
};
```

### Styling System

#### CSS Variables
```css
:root {
    --large-device-width: 850px;
    --primary-color: #0f172a;
    --secondary-color: #020617;
    --primary-text-color: #c7d1dd;
    --success-background: hsl(159, 82%, 24%);
    --success: hsl(160, 84%, 39%);
    --danger: #ef4444;
    --warning: #f59e0b;
    --border-color: #d1d7dc;
    --check-box-size: 20px;
    --check-box-color: var(--info-foreground);
}
```

#### Responsive Design
```css
/* Mobile devices */
@media (max-width: 767px) {
    input[type="radio"], label {
        cursor: default;
    }
    #quiz-container {
        margin-left: 8px;
        margin-right: 8px;
    }
}

/* Desktop devices */
@media (min-width: 768px) {
    body {
        display: flex;
        justify-content: center;
    }
    main {
        max-width: var(--large-device-width);
    }
}
```

## Coding Assignment Template

### Purpose
Displays programming exercises with instructions, test cases, and solutions in a structured format.

### Template Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Coding Assignment</title>
    <!-- Styling for code display -->
</head>
<body onload="main()">
    <h1 id="coding-title"></h1>
    
    <div>
        <h2>Instructions</h2>
        <div id="coding-instructions"></div>
    </div>
    
    <div>
        <h2>Test(s)</h2>
        <div id="coding-tests"></div>
    </div>
    
    <div>
        <h2>Solution(s)</h2>
        <div id="coding-solutions"></div>
    </div>
    
    <script>
        const quizData = __data_placeholder__;
        // Processing logic
    </script>
</body>
</html>
```

### Data Structure
```javascript
const quizData = {
    title: "Assignment Title",
    hasInstructions: true,
    hasTests: true,
    hasSolutions: true,
    instructions: "HTML instruction content",
    tests: [
        {
            content: "test code content"
        }
    ],
    solutions: [
        {
            content: "solution code content"
        }
    ]
};
```

### Code Rendering
```javascript
function renderCodeList(rootElement, codeList, className, titlePrefix) {
    for (var i = 0; i < codeList.length; i++) {
        var elem = codeList[i];
        var jsElem = document.createElement("div");
        jsElem.className = className;
        
        var jsElemTitle = document.createElement("h3");
        jsElemTitle.innerHTML = titlePrefix + " " + (i + 1);
        
        var jsElemBody = document.createElement("code");
        jsElemBody.className = "code-block black-block";
        jsElemBody.innerHTML = "<pre>" + elem.content + "</pre>";
        
        jsElem.appendChild(jsElemTitle);
        jsElem.appendChild(jsElemBody);
        rootElement.appendChild(jsElem);
    }
}
```

### Content Processing
```javascript
function main() {
    // Set title
    var codingTitle = document.getElementById("coding-title");
    codingTitle.innerHTML = quizData.title;
    
    // Process instructions
    var codingInstructions = document.getElementById("coding-instructions");
    if (quizData.hasInstructions) {
        codingInstructions.innerHTML = quizData.instructions;
    } else {
        codingInstructions.innerHTML = '<span class="italic-text">' + quizData.instructions + "</span>";
    }
    
    // Process tests
    var codingTests = document.getElementById("coding-tests");
    if (!quizData.hasTests) {
        codingTests.innerHTML = '<span class="italic-text">' + quizData.tests + "</span>";
    } else {
        renderCodeList(codingTests, quizData.tests, "coding-test", "Test");
    }
    
    // Process solutions
    var codingSolutions = document.getElementById("coding-solutions");
    if (!quizData.hasSolutions) {
        codingSolutions.innerHTML = '<span class="italic-text">' + quizData.solutions + "</span>";
    } else {
        renderCodeList(codingSolutions, quizData.solutions, "coding-solution", "Solution");
    }
}
```

## Template Processing Functions

### Quiz Processing
```python
def process_normal_quiz(quiz, lecture, chapter_dir):
    """
    Process normal quiz and generate HTML file.
    
    Args:
        quiz (dict): Quiz data with questions and metadata
        lecture (dict): Lecture information
        chapter_dir (str): Chapter directory path
        
    Process:
        1. Load quiz_template.html
        2. Prepare quiz data structure
        3. Replace __data_placeholder__ with JSON data
        4. Write HTML file to chapter directory
        
    Data Preparation:
        - Extract quiz metadata (title, description, pass percentage)
        - Format questions and answers
        - Include explanations and correct responses
    """

def process_coding_assignment(quiz, lecture, chapter_dir):
    """
    Process coding assignment and generate HTML file.
    
    Args:
        quiz (dict): Coding assignment data
        lecture (dict): Lecture information
        chapter_dir (str): Chapter directory path
        
    Process:
        1. Load coding_assignment_template.html
        2. Prepare assignment data structure
        3. Replace __data_placeholder__ with JSON data
        4. Write HTML file to chapter directory
        
    Data Preparation:
        - Extract instructions, tests, and solutions
        - Determine availability of each component
        - Format code content for display
    """
```

### Article Processing
```python
def process_article_asset(asset, lecture_title, chapter_dir):
    """
    Process article asset and generate HTML file.
    
    Args:
        asset (dict): Article asset data
        lecture_title (str): Lecture title
        chapter_dir (str): Chapter directory path
        
    Process:
        1. Load article_template.html
        2. Extract article body content
        3. Replace template placeholders
        4. Write HTML file to chapter directory
        
    Template Replacement:
        - __title_placeholder__: Lecture title (stripped of numbering)
        - __data_placeholder__: Article HTML body content
    """
```

## Template Styling Guidelines

### Color Scheme
- **Primary**: Dark theme with high contrast
- **Success**: Green tones for correct answers
- **Error**: Red tones for incorrect answers
- **Warning**: Orange/yellow for warnings
- **Info**: Blue tones for information

### Typography
- **Headers**: System fonts with fallbacks
- **Body**: Readable font sizes with proper line height
- **Code**: Monospace fonts for code blocks
- **UI Elements**: Consistent sizing and spacing

### Responsive Behavior
- **Mobile**: Touch-friendly interfaces, simplified layouts
- **Desktop**: Full feature set, optimal spacing
- **Print**: Clean, printer-friendly styles

### Accessibility Features
- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: Proper ARIA labels and semantic HTML
- **High Contrast**: Sufficient color contrast ratios
- **Focus Indicators**: Clear focus states for interactive elements

## Template Customization

### Modifying Templates
1. **Backup Original**: Always backup original templates
2. **Test Changes**: Verify functionality after modifications
3. **Maintain Placeholders**: Keep placeholder strings intact
4. **Validate HTML**: Ensure valid HTML structure
5. **Test Responsiveness**: Verify mobile and desktop layouts

### Adding New Templates
1. **Create Template File**: Add new HTML template to templates/
2. **Define Placeholders**: Use consistent placeholder naming
3. **Add Processing Function**: Create corresponding processing function
4. **Update Content Detection**: Modify content type detection logic
5. **Test Integration**: Verify end-to-end functionality