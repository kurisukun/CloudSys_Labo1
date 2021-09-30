<?php

namespace App\Http\Controllers;

use App\Models\Todo;
use Illuminate\Http\Request;

class ApiController extends Controller
{

    public function index()
    {
        return Todo::all();
    }

    public function add(Request $request) {
        $request->validate([
            'title' => 'required',
            'is_done' => 'required',
        ]);
        $todo = new Todo($request->all());
        $todo->save();
    }

    public function remove(int $id) {
        $todo = Todo::findOrFail($id);
        $todo->delete();
    }

    public function toggle(int $id) {
        $todo = Todo::findOrFail($id);
        $todo->is_done = !$todo->is_done;
        $todo->save();
    }

}
