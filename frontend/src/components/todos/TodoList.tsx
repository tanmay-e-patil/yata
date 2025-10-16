import React, { useState, useEffect } from 'react';
import { Todo, TodoCreate } from '../../types';
import { apiService } from '../../services/api';
import TodoItem from './TodoItem';
import TodoForm from './TodoForm';

const TodoList: React.FC = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchTodos = async () => {
    try {
      const fetchedTodos = await apiService.getTodos();
      setTodos(fetchedTodos);
    } catch (error) {
      console.error('Failed to fetch todos:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTodos();
  }, []);

  const handleCreateTodo = async (todo: TodoCreate) => {
    try {
      const newTodo = await apiService.createTodo(todo);
      setTodos([newTodo, ...todos]);
    } catch (error) {
      console.error('Failed to create todo:', error);
    }
  };

  const handleUpdateTodo = async (id: string, updatedTodo: Partial<Todo>) => {
    try {
      const updated = await apiService.updateTodo(id, updatedTodo);
      setTodos(todos.map(todo => todo.id === id ? updated : todo));
    } catch (error) {
      console.error('Failed to update todo:', error);
    }
  };

  const handleDeleteTodo = async (id: string) => {
    try {
      await apiService.deleteTodo(id);
      setTodos(todos.filter(todo => todo.id !== id));
    } catch (error) {
      console.error('Failed to delete todo:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">My Todos</h1>
      
      <TodoForm onSubmit={handleCreateTodo} />
      
      <div className="mt-6 space-y-2">
        {todos.length === 0 ? (
          <p className="text-center text-gray-500 py-8">
            No todos yet. Create your first todo above!
          </p>
        ) : (
          todos.map(todo => (
            <TodoItem
              key={todo.id}
              todo={todo}
              onUpdate={handleUpdateTodo}
              onDelete={handleDeleteTodo}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default TodoList;