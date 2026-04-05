# Angular NG0100: ExpressionChangedAfterItHasBeenCheckedError - Complete Guide

## Overview

The `NG0100: ExpressionChangedAfterItHasBeenCheckedError` is one of the most common and misunderstood errors in Angular applications. This error **only appears in development mode** and is a safety mechanism to prevent infinite change detection loops in production.

## What Causes NG0100?

Angular uses **unidirectional data flow** (top-down). To ensure the UI accurately reflects the application state, Angular runs change detection in **two passes** during development:

1. **First pass**: Reads component properties and updates the DOM
2. **Second pass**: Immediately verifies that no values changed during the first pass

If a property changes between these two passes, Angular throws NG0100 to alert you of a potential architectural issue.

## The Real Culprit: Material Components and Async Updates

### The Mystery of `-1` to `1`

When you see an error like:
```
Previous value: '-1'. Current value: '1'
```

This is **NOT** about your boolean properties (like `loading` or `saving`). This is about **internal state** in Material components, particularly `<mat-select>`.

### What Actually Happens

Consider this common pattern:

```typescript
// Component
availableVersions: Version[] = [];
selectedVersion: string = 'latest';

loadData(): void {
  this.service.getData().subscribe(response => {
    // Both properties updated simultaneously
    this.availableVersions = response.versions;
    this.selectedVersion = response.selected;
    this.cdr.markForCheck();
  });
}
```

```html
<!-- Template -->
<mat-select [(ngModel)]="selectedVersion">
  @for (v of availableVersions; track v.id) {
    <mat-option [value]="v.id">{{ v.name }}</mat-option>
  }
</mat-select>
```

**The Problem:**

1. Angular's `@for` loop **instantly destroys and rebuilds** the `<mat-option>` DOM nodes when `availableVersions` changes
2. Simultaneously, `<mat-select>` evaluates its `[(ngModel)]="selectedVersion"`
3. For a microsecond, `<mat-select>` cannot find the matching option (DOM is being rebuilt), so its internal selected index defaults to `-1`
4. A fraction later in the **same change detection cycle**, options finish rendering and `<mat-select>` updates its index to `1` (or whatever the correct index is)
5. Angular's second verification pass detects this internal change and throws NG0100

## Why Common "Solutions" Don't Work

### ❌ `setTimeout(() => this.load(), 0)`
```typescript
this.service.save().subscribe(() => {
  setTimeout(() => this.load(), 0); // Still triggers NG0100
});
```

**Why it fails:** `setTimeout` pushes execution to the macrotask queue, but when `load()` sets `this.loading = true`, it's still within a change detection cycle triggered by the timeout itself.

### ❌ `Promise.resolve().then(() => this.load())`
```typescript
this.service.save().subscribe(() => {
  Promise.resolve().then(() => this.load()); // Still triggers NG0100
});
```

**Why it fails:** Promises push to the microtask queue, which executes before the next change detection. The timing issue remains.

### ❌ `NgZone.run()`
```typescript
this.ngZone.run(() => {
  this.data = response; // Doesn't work with Fetch API
});
```

**Why it fails:** When using `provideHttpClient(withFetch())`, the Fetch API runs **outside Angular's zone**, so `NgZone.run()` has no effect.

## ✅ The Correct Solution: RxJS Operators

The root issue is **mixing Promises/setTimeout with RxJS Observables**. This breaks Angular's execution context predictability.

### Pattern: Save → Reload Data

**❌ Wrong (causes NG0100):**
```typescript
save(): void {
  this.saving = true;
  
  this.service.save(data).subscribe({
    next: () => {
      this.saving = false;
      this.load(); // Triggers NG0100
    }
  });
}

load(): void {
  this.loading = true; // This change happens during change detection
  this.service.load().subscribe(response => {
    this.data = response;
    this.loading = false;
    this.cdr.markForCheck();
  });
}
```

**✅ Correct (no NG0100):**
```typescript
import { switchMap, tap, catchError } from 'rxjs/operators';
import { EMPTY } from 'rxjs';

save(): void {
  this.saving = true;
  this.cdr.markForCheck(); // Notify before async operation
  
  this.service.save(data).pipe(
    tap(() => {
      // Handle immediate aftermath of save
      this.saving = false;
      this.loading = true;
      this.cdr.markForCheck();
    }),
    // Chain the reload automatically
    switchMap(() => this.service.load()),
    catchError((err) => {
      this.saving = false;
      this.loading = false;
      this.cdr.markForCheck();
      return EMPTY; // Stop stream on error
    })
  ).subscribe({
    next: (response) => this.applyState(response)
  });
}

// Centralized state update
private applyState(response: any): void {
  this.data = response.data;
  this.items = response.items;
  this.selected = response.selected;
  
  this.loading = false;
  this.cdr.markForCheck(); // Single update after all assignments
}
```

### Why This Works

1. **Stays in RxJS context**: No mixing of Promises/setTimeout with Observables
2. **Predictable execution**: `switchMap` chains operations in a controlled manner
3. **Proper timing**: State changes happen at the right moments in the change detection cycle
4. **Centralized updates**: `applyState()` updates all properties together, then triggers one `markForCheck()`

## Key Principles

### 1. Always Call `markForCheck()` Before Async Operations

```typescript
loadData(): void {
  this.loading = true;
  this.cdr.markForCheck(); // ← Critical with Fetch API
  
  this.service.getData().subscribe(/* ... */);
}
```

**Why:** With `provideHttpClient(withFetch())`, the Fetch API runs outside Angular's zone. You must manually trigger change detection.

### 2. Use RxJS Operators for Sequential Operations

```typescript
// ✅ Good: Chain with switchMap
this.service.save(data).pipe(
  switchMap(() => this.service.load())
).subscribe(/* ... */);

// ❌ Bad: Nested subscribes
this.service.save(data).subscribe(() => {
  this.service.load().subscribe(/* ... */);
});
```

### 3. Centralize State Updates

```typescript
// ✅ Good: Single method updates all related state
private applyState(response: any): void {
  this.prop1 = response.prop1;
  this.prop2 = response.prop2;
  this.prop3 = response.prop3;
  this.loading = false;
  this.cdr.markForCheck(); // One call after all updates
}

// ❌ Bad: Scattered updates
this.prop1 = response.prop1;
this.cdr.markForCheck();
this.prop2 = response.prop2;
this.cdr.markForCheck();
```

### 4. Handle Errors Properly

```typescript
this.service.save(data).pipe(
  switchMap(() => this.service.load()),
  catchError((err) => {
    // Reset all state flags
    this.saving = false;
    this.loading = false;
    this.cdr.markForCheck();
    return EMPTY; // Prevents error propagation
  })
).subscribe(/* ... */);
```

## Real-World Example: Config Panel

This example demonstrates the complete pattern for a configuration management panel:

```typescript
import { Component, inject, ChangeDetectorRef } from '@angular/core';
import { switchMap, tap, catchError } from 'rxjs/operators';
import { EMPTY } from 'rxjs';

@Component({
  selector: 'app-config-panel',
  standalone: true,
  template: `
    @if (loading) {
      <mat-spinner></mat-spinner>
    }
    
    <mat-select [(ngModel)]="selectedVersion">
      @for (v of availableVersions; track v.id) {
        <mat-option [value]="v.id">Version {{ v.id }}</mat-option>
      }
    </mat-select>
    
    <button (click)="save()" [disabled]="saving">Save</button>
  `
})
export class ConfigPanel {
  private service = inject(ConfigService);
  private cdr = inject(ChangeDetectorRef);
  
  config: Config = {};
  availableVersions: Version[] = [];
  selectedVersion: string = 'latest';
  saving = false;
  loading = false;

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.cdr.markForCheck(); // Before async operation
    
    this.service.getConfig().subscribe({
      next: (response) => this.applyConfigState(response),
      error: (err) => {
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }

  save(): void {
    this.saving = true;
    this.cdr.markForCheck();
    
    this.service.saveConfig(this.config).pipe(
      tap(() => {
        this.saving = false;
        this.loading = true;
        this.cdr.markForCheck();
      }),
      switchMap(() => this.service.getConfig()), // Chain reload
      catchError((err) => {
        this.saving = false;
        this.loading = false;
        this.cdr.markForCheck();
        return EMPTY;
      })
    ).subscribe({
      next: (response) => this.applyConfigState(response)
    });
  }

  // Centralized state update
  private applyConfigState(response: ConfigResponse): void {
    this.config = response.config;
    this.availableVersions = response.versions;
    this.selectedVersion = response.selected;
    
    this.loading = false;
    this.cdr.markForCheck(); // Single call after all updates
  }
}
```

## Debugging NG0100

### 1. Identify the Actual Property

The error message shows internal component state, not your properties:
```
Previous value: '-1'. Current value: '1'
```

This is likely `<mat-select>` internal index, not your `loading` boolean.

### 2. Check for Simultaneous Array + Selection Updates

```typescript
// ❌ Problem: Both updated at once
this.items = response.items;
this.selectedItem = response.selected;

// ✅ Solution: Update in centralized method with proper timing
private applyState(response: any): void {
  this.items = response.items;
  this.selectedItem = response.selected;
  this.cdr.markForCheck();
}
```

### 3. Look for Nested Subscribes

```typescript
// ❌ Bad: Nested subscribes cause timing issues
this.service.save().subscribe(() => {
  this.service.load().subscribe(/* ... */);
});

// ✅ Good: Use switchMap
this.service.save().pipe(
  switchMap(() => this.service.load())
).subscribe(/* ... */);
```

## Summary

**The NG0100 error is not about your boolean flags.** It's about:

1. **Material components** (like `<mat-select>`) updating their internal state when you rebuild their options
2. **Mixing Promises/setTimeout with RxJS**, breaking execution context
3. **Not using RxJS operators** for sequential operations

**The solution:**
- Use `switchMap` to chain save → reload operations
- Call `markForCheck()` before async operations (critical with Fetch API)
- Centralize state updates in a single method
- Stay within RxJS context—don't mix with Promises/setTimeout

This pattern works for any "save → reload" flow in Angular 21+ with Fetch API.

