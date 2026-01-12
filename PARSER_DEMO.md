# 🎯 ORC Parser Output Demonstration

This shows **exactly what each parser extracts** from real code examples.

---

## 1. TypeScript Parser

**Input File:** `user.ts`
```typescript
export interface User {
    id: number;
    name: string;
    email?: string;
}

export type UserRole = 'admin' | 'user';

export enum Status {
    Active,
    Inactive,
    Pending
}

@Component({
    selector: 'app-user'
})
export class UserComponent {
    private userId: number;
    
    constructor() {}
}
```

**Parser Output:**
```json
{
    "files": {
        "user.ts": {
            "language": "typescript",
            "loc": 24,
            "typescript_features": {
                "interfaces": 1,
                "type_aliases": 1,
                "enums": 1,
                "decorators": 1,
                "type_imports": 0,
                "namespaces": 0
            }
        }
    },
    "interfaces": {
        "user.ts::User": {
            "id": "user.ts::User",
            "name": "User",
            "file": "user.ts",
            "line": 1,
            "kind": "interface",
            "properties": [
                {"name": "id", "optional": false, "type": "number"},
                {"name": "name", "optional": false, "type": "string"},
                {"name": "email", "optional": true, "type": "string"}
            ]
        }
    },
    "type_aliases": {
        "user.ts::UserRole": {
            "id": "user.ts::UserRole",
            "name": "UserRole",
            "file": "user.ts",
            "line": 7,
            "kind": "type_alias",
            "definition": "'admin' | 'user'"
        }
    },
    "enums": {
        "user.ts::Status": {
            "id": "user.ts::Status",
            "name": "Status",
            "file": "user.ts",
            "line": 9,
            "kind": "enum",
            "values": ["Active", "Inactive", "Pending"]
        }
    },
    "decorators": [
        {"name": "Component", "line": 15, "full_match": "@Component({...})"}
    ],
    "classes": {
        "user.ts::UserComponent": {
            "name": "UserComponent",
            "line": 18,
            "kind": "class"
        }
    }
}
```

---

## 2. React Parser

**Input File:** `UserProfile.jsx`
```jsx
import React, { useState, useEffect } from 'react';

const UserProfile = ({ userId, onUpdate }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetchUser(userId);
    }, [userId]);
    
    return (
        <div className="profile">
            <UserAvatar user={user} />
            <UserDetails user={user} />
        </div>
    );
};

export default React.memo(UserProfile);
```

**Parser Output:**
```json
{
    "files": {
        "UserProfile.jsx": {
            "language": "react",
            "loc": 19,
            "react_features": {
                "function_components": 1,
                "class_components": 0,
                "hooks_used": 2,
                "jsx_elements": 2,
                "contexts": 0,
                "hocs": 0
            }
        }
    },
    "function_components": {
        "UserProfile.jsx::UserProfile": {
            "id": "UserProfile.jsx::UserProfile",
            "name": "UserProfile",
            "file": "UserProfile.jsx",
            "line": 3,
            "kind": "function_component",
            "has_jsx": true
        }
    },
    "hooks": [
        {"name": "useState", "line": 4},
        {"name": "useState", "line": 5},
        {"name": "useEffect", "line": 7}
    ],
    "jsx_elements": ["UserAvatar", "UserDetails"],
    "props": [
        {
            "line": 3,
            "props": ["userId", "onUpdate"],
            "destructured": true
        }
    ],
    "memo_components": [
        {"component": "UserProfile", "line": 19}
    ]
}
```

---

## 3. Django Parser

**Input File:** `models.py`
```python
from django.db import models
from django.contrib.auth.models import User

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

**Parser Output:**
```json
{
    "files": {
        "models.py": {
            "language": "python",
            "framework": "django",
            "loc": 20,
            "django_features": {
                "models": 2,
                "views": 0,
                "url_patterns": 0,
                "forms": 0,
                "admin_registrations": 0,
                "serializers": 0,
                "managers": 0,
                "signals": 0,
                "template_tags": 0
            }
        }
    },
    "django_models": {
        "models.py::BlogPost": {
            "id": "models.py::BlogPost",
            "name": "BlogPost",
            "file": "models.py",
            "line": 4,
            "kind": "django_model",
            "fields": [
                {"name": "title", "type": "CharField"},
                {"name": "content", "type": "TextField"},
                {"name": "author", "type": "ForeignKey"},
                {"name": "created_at", "type": "DateTimeField"},
                {"name": "published", "type": "BooleanField"}
            ]
        },
        "models.py::Comment": {
            "id": "models.py::Comment",
            "name": "Comment",
            "file": "models.py",
            "line": 17,
            "kind": "django_model",
            "fields": [
                {"name": "post", "type": "ForeignKey"},
                {"name": "text", "type": "TextField"},
                {"name": "created_at", "type": "DateTimeField"}
            ]
        }
    }
}
```

---

## 4. FastAPI Parser

**Input File:** `api.py`
```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    return {"id": user_id, "username": "john", "email": "john@example.com"}

@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    return {"id": 1, "username": user.username, "email": user.email}
```

**Parser Output:**
```json
{
    "files": {
        "api.py": {
            "language": "python",
            "framework": "fastapi",
            "loc": 22,
            "fastapi_features": {
                "routes": 2,
                "pydantic_models": 2,
                "dependencies": 0,
                "websockets": 0,
                "middleware": 0,
                "routers": 0
            }
        }
    },
    "fastapi_routes": [
        {
            "path": "/users/{user_id}",
            "method": "GET",
            "line": 16,
            "function": "get_user",
            "path_params": ["user_id"]
        },
        {
            "path": "/users",
            "method": "POST",
            "line": 20,
            "function": "create_user",
            "path_params": []
        }
    ],
    "fastapi_models": {
        "api.py::UserCreate": {
            "id": "api.py::UserCreate",
            "name": "UserCreate",
            "file": "api.py",
            "line": 6,
            "kind": "pydantic_model",
            "fields": [
                {"name": "username", "type": "str"},
                {"name": "email", "type": "str"},
                {"name": "password", "type": "str"}
            ]
        },
        "api.py::UserResponse": {
            "id": "api.py::UserResponse",
            "name": "UserResponse",
            "file": "api.py",
            "line": 11,
            "kind": "pydantic_model",
            "fields": [
                {"name": "id", "type": "int"},
                {"name": "username", "type": "str"},
                {"name": "email", "type": "str"}
            ]
        }
    },
    "fastapi_response_models": [
        {"model": "UserResponse", "line": 16},
        {"model": "UserResponse", "line": 20}
    ]
}
```

---

## 5. SCSS Parser

**Input File:** `styles.scss`
```scss
$primary-color: #007bff;
$font-size-base: 16px;

@mixin button-style($bg-color) {
    background-color: $bg-color;
    padding: 10px 20px;
    border-radius: 4px;
}

@function calculate-spacing($base) {
    @return $base * 1.5;
}

.button {
    @include button-style($primary-color);
    font-size: $font-size-base;
    
    &:hover {
        background-color: darken($primary-color, 10%);
    }
}

%shared-icon {
    display: inline-block;
    width: 20px;
    height: 20px;
}

.icon-user {
    @extend %shared-icon;
    background-image: url('user.svg');
}
```

**Parser Output:**
```json
{
    "files": {
        "styles.scss": {
            "language": "scss",
            "loc": 32,
            "scss_features": {
                "variables": 2,
                "mixins": 1,
                "functions": 1,
                "imports": 0,
                "includes": 1,
                "extends": 1,
                "placeholders": 1,
                "classes": 3,
                "control_directives": 1
            }
        }
    },
    "scss_variables": {
        "styles.scss::primary-color": {
            "id": "styles.scss::primary-color",
            "name": "$primary-color",
            "file": "styles.scss",
            "line": 1,
            "kind": "scss_variable"
        },
        "styles.scss::font-size-base": {
            "id": "styles.scss::font-size-base",
            "name": "$font-size-base",
            "file": "styles.scss",
            "line": 2,
            "kind": "scss_variable"
        }
    },
    "scss_mixins": {
        "styles.scss::button-style": {
            "id": "styles.scss::button-style",
            "name": "button-style",
            "file": "styles.scss",
            "line": 4,
            "kind": "scss_mixin"
        }
    },
    "functions": {
        "styles.scss::calculate-spacing": {
            "id": "styles.scss::calculate-spacing",
            "name": "calculate-spacing",
            "file": "styles.scss",
            "line": 10,
            "kind": "scss_function"
        }
    },
    "scss_includes": [
        {"mixin": "button-style", "line": 15}
    ],
    "scss_extends": [
        {"selector": "%shared-icon", "line": 29}
    ],
    "classes": {
        "styles.scss::.button": {
            "name": ".button",
            "line": 14,
            "kind": "css_class"
        },
        "styles.scss::%shared-icon": {
            "name": "%shared-icon",
            "line": 23,
            "kind": "scss_placeholder"
        },
        "styles.scss::.icon-user": {
            "name": ".icon-user",
            "line": 28,
            "kind": "css_class"
        }
    }
}
```

---

## 6. Markdown Parser

**Input File:** `README.md`
```markdown
# Project Title

A brief description of the project.

## Features

- Fast performance
- Easy to use
- Well documented

## Installation

```bash
npm install my-package
```

## Usage

```javascript
import { MyComponent } from 'my-package';

const app = new MyComponent();
app.run();
```

For more info, see [documentation](./docs/api.md).

![Logo](./assets/logo.png)
```

**Parser Output:**
```json
{
    "files": {
        "README.md": {
            "language": "markdown",
            "loc": 28,
            "markdown_features": {
                "headings": 4,
                "code_blocks": 2,
                "links": 1,
                "images": 1,
                "lists": 3,
                "blockquotes": 0,
                "tables": 0,
                "has_frontmatter": false
            }
        }
    },
    "markdown_headings": {
        "README.md::h1::project-title": {
            "name": "Project Title",
            "line": 1,
            "kind": "heading_h1",
            "level": 1
        },
        "README.md::h2::features": {
            "name": "Features",
            "line": 5,
            "kind": "heading_h2",
            "level": 2
        },
        "README.md::h2::installation": {
            "name": "Installation",
            "line": 11,
            "kind": "heading_h2",
            "level": 2
        },
        "README.md::h2::usage": {
            "name": "Usage",
            "line": 17,
            "kind": "heading_h2",
            "level": 2
        }
    },
    "markdown_code_blocks": [
        {
            "language": "bash",
            "code": "npm install my-package",
            "line": 13,
            "length": 1
        },
        {
            "language": "javascript",
            "code": "import { MyComponent } from 'my-package';\\n\\nconst app = new MyComponent();\\napp.run();",
            "line": 19,
            "length": 4
        }
    ],
    "markdown_links": {
        "inline": [
            {"text": "documentation", "url": "./docs/api.md", "line": 26}
        ],
        "reference": []
    },
    "markdown_images": [
        {"alt": "Logo", "url": "./assets/logo.png", "line": 28}
    ],
    "markdown_lists": {
        "unordered": 3,
        "ordered": 0,
        "total": 3
    }
}
```

---

## 7. JSON Parser

**Input File:** `package.json`
```json
{
  "name": "my-app",
  "version": "1.0.0",
  "scripts": {
    "start": "node index.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.18.0",
    "lodash": "^4.17.21"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  }
}
```

**Parser Output:**
```json
{
    "files": {
        "package.json": {
            "language": "json",
            "loc": 14,
            "json_features": {
                "valid": true,
                "schema_type": "package.json",
                "top_level_keys": 5,
                "depth": 2,
                "objects": 4,
                "arrays": 0
            }
        }
    },
    "json_valid": true,
    "json_schema_type": "package.json",
    "json_top_keys": ["name", "version", "scripts", "dependencies", "devDependencies"],
    "json_depth": 2
}
```

---

## 8. YAML Parser

**Input File:** `.github/workflows/ci.yml`
```yaml
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: npm test
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: ./deploy.sh
```

**Parser Output:**
```json
{
    "files": {
        ".github/workflows/ci.yml": {
            "language": "yaml",
            "loc": 20,
            "yaml_features": {
                "valid": true,
                "document_type": "github_actions",
                "top_level_keys": 3,
                "depth": 4,
                "mappings": 12,
                "sequences": 4
            }
        }
    },
    "yaml_valid": true,
    "yaml_document_type": "github_actions",
    "yaml_top_keys": ["name", "on", "jobs"],
    "yaml_depth": 4
}
```

---

## 🎯 Summary

### **What Gets Extracted:**

| Parser | Key Features Extracted |
|--------|------------------------|
| **TypeScript** | Interfaces, types, enums, decorators, generics, namespaces |
| **React** | Components, hooks, props, JSX elements, memo/lazy, HOCs |
| **Django** | Models + fields, views, URLs, forms, admin, serializers |
| **FastAPI** | Routes, Pydantic models + fields, dependencies, WebSockets |
| **SCSS** | Variables, mixins, functions, imports, extends, placeholders |
| **Markdown** | Headings, code blocks, links, images, lists, tables |
| **JSON** | Schema type, structure depth, top keys, validity |
| **YAML** | Document type, structure depth, mappings, sequences |

### **How It's Used:**

1. **When you run `orc index`** → All files are parsed automatically
2. **Parser detects file type** → Uses appropriate parser
3. **Framework detection** → Django/FastAPI/Tailwind auto-detected
4. **Structure extracted** → All features cataloged
5. **Cached for speed** → Unchanged files skip re-parsing

### **Benefits:**

- ✅ **Accurate search** - Find specific interfaces, routes, models
- ✅ **Better context** - AI knows exact code structures
- ✅ **Smart analysis** - Understand dependencies, relationships
- ✅ **Framework-aware** - Recognizes Django models, FastAPI endpoints

---

## 🚀 Try It Yourself!

```bash
# Index your codebase
orc index /path/to/your/project

# The parsers will extract all this structure automatically!
```

Your ORC now has **industrial-grade parsing** for 12+ languages! 🎉
