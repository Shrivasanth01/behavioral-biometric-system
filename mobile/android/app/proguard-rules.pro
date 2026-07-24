-keep class com.securebank.** { *; }
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }

-keepattributes *Annotation*
-keepattributes SourceFile,LineNumberTable

-dontwarn com.google.errorprone.annotations.**
-dontwarn javax.annotation.**
-dontwarn javax.inject.**
-dontwarn sun.misc.Unsafe

-keep class * extends java.util.ListResourceBundle {
    protected Object[][] getContents();
}

-keep class * implements com.google.gson.TypeAdapterFactory
-keep class * implements com.google.gson.JsonSerializer
-keep class * implements com.google.gson.JsonDeserializer

-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}

-keep class kotlin.Metadata { *; }
-keep class kotlin.Unit { *; }
