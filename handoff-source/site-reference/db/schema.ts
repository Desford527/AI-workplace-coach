import { sqliteTable, text, integer, primaryKey } from 'drizzle-orm/sqlite-core';
export const documents = sqliteTable('documents', {
 owner: text('owner').notNull(),
 key: text('key').notNull(),
 payload: text('payload').notNull(),
 revision: integer('revision').notNull().default(1),
 updated: text('updated').notNull(),
}, t => [primaryKey({ columns: [t.owner, t.key] })]);
